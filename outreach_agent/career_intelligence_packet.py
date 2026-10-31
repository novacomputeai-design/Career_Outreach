"""V2.1 bounded public-only opportunity review packet.

No network, private Windows store, Google Drive, external applications or sender.
This is a research handoff, NOT source truth or contact readiness.
"""
from __future__ import annotations
from datetime import date
import json
import re
from pathlib import Path
from .career_intelligence import audit_packet
from .project_scope import PROJECT_ID

SCHEMA_VERSION = "2.1"
MAX_PACKET_BYTES = 131072
MAX_OPPORTUNITIES = 20
KEYS = {"schema_version", "project_id", "run_id", "date_local", "opportunities"}
FORBIDDEN = {
    "private_email", "personal_phone", "email_body", "private_notes",
    "memory_key", "identity_key", "outreach_state_key", "dpapi_token",
    "send_authorization", "private_history", "conversation_history",
}


def _safe_public(value):
    if isinstance(value, dict):
        if FORBIDDEN.intersection(value.keys()):
            raise ValueError("Private fields not allowed in public research packet")
        for child in value.values():
            _safe_public(child)
    elif isinstance(value, list):
        for child in value:
            _safe_public(child)


def build_review_packet(packet):
    if not isinstance(packet, dict) or set(packet) != KEYS:
        raise ValueError("Unexpected research packet shape")
    if packet["project_id"] != PROJECT_ID or packet["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Wrong personal career project/schema")
    if not isinstance(packet["run_id"], str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,99}", packet["run_id"]):
        raise ValueError("Invalid run_id")
    try:
        d = date.fromisoformat(packet["date_local"])
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid Phoenix date") from exc
    if d > date.today():
        raise ValueError("Future run date")
    opportunities = packet["opportunities"]
    if not isinstance(opportunities, list) or len(opportunities) > MAX_OPPORTUNITIES:
        raise ValueError("Invalid opportunity count")
    _safe_public(packet)
    summary = audit_packet(opportunities)
    return {
        "schema_version": SCHEMA_VERSION, "project_id": PROJECT_ID,
        "run_id": packet["run_id"], "date_local": d.isoformat(),
        "research_summary": summary,
        "native_skills_verified": False,
        "source_truth_independently_verified": False,
        "private_history_checked": False,
        "contact_ready": 0,
        "outbound_sent": 0, "applications_submitted": 0,
        "status": "RESEARCH_REVIEW_ONLY_NOT_ENGAGEMENT_READY",
    }


def assess_private_files(source, destination):
    root = Path(__file__).resolve().parents[1]
    source, destination = Path(source).resolve(), Path(destination).resolve()
    if source == destination:
        raise ValueError("Input and output must differ")
    for path in (source, destination):
        if path == root or root in path.parents:
            raise ValueError("Research files must remain outside PUBLIC Git")
        if path.suffix.lower() != ".json":
            raise ValueError("JSON only")
    if not source.is_file() or source.stat().st_size > MAX_PACKET_BYTES:
        raise ValueError("Missing or oversized research packet")
    if destination.exists():
        raise FileExistsError("Never overwrite a research review report")
    payload = json.loads(source.read_text(encoding="utf-8-sig"))
    report = build_review_packet(payload)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as fh:
        json.dump(report, fh, indent=2, ensure_ascii=False)
        fh.write("\n")
    return report
