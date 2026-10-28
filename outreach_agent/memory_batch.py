"""Operator-only, read-minimized batch relationship screening.

Not a Codex sandbox broker. Names supplied in private local JSON file, NOT Git.
No writing to SQLite, no network, no model-driven authorization.
"""
from __future__ import annotations
import json
from pathlib import Path
from urllib.parse import urlparse
from .state import normalized

MAX_BYTES = 65536
MAX_PEOPLE = 100

def screen_batch(store, input_file: str | Path) -> dict:
    path = Path(input_file)
    if not path.is_file():
        raise FileNotFoundError("Private batch file unavailable; do not infer novelty")
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Private batch input too large (64 KiB max)")
    try:
        incoming = json.loads(path.read_text(encoding="utf-8-sig"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid private batch JSON") from exc
    if not isinstance(incoming, list) or not 1 <= len(incoming) <= MAX_PEOPLE:
        raise ValueError("Expected JSON list with 1..100 names or identity objects")

    clean = []
    for entry in incoming:
        if isinstance(entry, str):
            name, profile = entry, None
        elif isinstance(entry, dict) and set(entry).issubset({"person_name","profile_url"}):
            name, profile = entry.get("person_name"), entry.get("profile_url")
        else:
            raise ValueError("Each item must be a name or {person_name, profile_url} object")
        if not isinstance(name, str):
            raise ValueError("Missing person_name")
        name = " ".join(name.strip().split())
        if not 3 <= len(name) <= 240 or len(name.split()) < 2 or any(ord(c) < 32 for c in name):
            raise ValueError("Invalid individual full name")
        if profile in ("", None):
            profile = None
        elif not isinstance(profile, str) or len(profile)>2048:
            raise ValueError("Invalid individual profile URL")
        elif (lambda u: u.scheme != "https" or not u.hostname or u.username is not None or u.password is not None)(urlparse(profile)):
            raise ValueError("Individual profile URL must be a valid HTTPS URL")
        clean.append((name,profile))

    seen_names = set()
    rows = []
    for name, profile in clean:
        norm = normalized(name)
        if norm in seen_names:
            rows.append({"person_name":name, "result":"DUPLICATE_IN_BATCH_HOLD",
                         "novelty":"UNVERIFIED", "granted_contact_readiness":False})
            continue
        seen_names.add(norm)
        record = store.check_relationship(name, profile_url=profile)
        # Ensure output never contains raw private relationship notes or profiles.
        minimal = {"person_name": name, "result":record["result"],
                   "novelty":record["novelty"],
                   "granted_contact_readiness":False}
        if "user_reported_relationship" in record:
            minimal["user_reported_relationship"] = record["user_reported_relationship"]
        if "suppressed" in record:
            minimal["suppressed"] = record["suppressed"]
        rows.append(minimal)
    return {"verification_level":"OPERATOR_PROTECTED_LOCAL_STORE_ONLY",
            "complete_cross_channel_history_verified":False,
            "new_contact_ready_granted":0,
            "people_checked":len(rows),
            "results":rows,
            "caveat":"NOT_FOUND_IN_LOCAL_STORE does not prove a person is new. Do not auto-contact or count anyone as contact-ready."}
