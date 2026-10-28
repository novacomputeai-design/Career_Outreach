#!/usr/bin/env python3
"""Offline structural preflight and daily quota filter. No web, CRM, or sending.
Input evidence is assumed supplied by a separate research agent; THIS SCRIPT DOES
NOT INDEPENDENTLY VERIFY THE TRUTH OF LINKS OR CLAIMS.
"""
import argparse
import datetime as dt
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from outreach_agent.project_scope import scope_reasons
from urllib.parse import urlparse

CAPS = {"alignment": 30, "influence": 25, "conversation": 20, "reachability": 15, "geography": 10}
TARGET = 20

def valid_url(value):
    if not isinstance(value, str):
        return False
    p = urlparse(value)
    return p.scheme == "https" and bool(p.netloc) and not any(ch.isspace() for ch in value)

def evaluate(candidate, known_ids, seen_ids=None):
    """Return (eligible, score, reasons); structural only, not evidence verification."""
    seen_ids = seen_ids if seen_ids is not None else set()
    errors = scope_reasons(candidate, require_project_id=True)
    if not isinstance(candidate, dict):
        return False, 0, ["candidate_not_object"]
    person_id = candidate.get("person_id")
    if not isinstance(person_id, str) or not person_id.strip():
        errors.append("missing_stable_person_id")
    elif person_id in known_ids or person_id in seen_ids:
        errors.append("duplicate_person")
    for key in ("person_name", "organization", "current_title", "why_connect"):
        value = candidate.get(key)
        if not isinstance(value, str) or len(value.strip()) < (25 if key == "why_connect" else 3):
            errors.append("invalid_" + key)
    for key in ("role_source_url", "reason_source_url", "contact_route_url"):
        if not valid_url(candidate.get(key)):
            errors.append("invalid_" + key)
    if candidate.get("route_type") not in ("DIRECT", "INDIRECT", "MANUAL"):
        errors.append("invalid_route_type")
    for key in ("role_verified", "contact_route_verified", "history_checked"):
        if candidate.get(key) is not True:
            errors.append("required_gate_" + key)
    if candidate.get("suppressed") is not False:
        errors.append("suppressed_or_unconfirmed")
    if candidate.get("novelty") != "NEW":
        errors.append("not_confirmed_new")
    date_string = candidate.get("observed_on")
    try:
        observed = dt.date.fromisoformat(date_string)
        if observed > dt.datetime.now(dt.timezone.utc).date():
            errors.append("future_observation")
    except (TypeError, ValueError):
        errors.append("invalid_observed_on")
    scores = candidate.get("scores", {})
    score = 0
    if not isinstance(scores, dict):
        errors.append("invalid_scores")
    else:
        for category, maximum in CAPS.items():
            value = scores.get(category)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or value < 0 or value > maximum:
                errors.append("invalid_score_" + category)
            else:
                score += value
    if score < 70:
        errors.append("below_score_threshold")
    return not errors, score, errors

def build_brief(candidates, known_ids, target=TARGET):
    results, rejected, seen_ids = [], [], set()
    for candidate in candidates:
        ok, score, errors = evaluate(candidate, known_ids, seen_ids)
        if ok:
            record = dict(candidate)
            record["score_total"] = score
            results.append(record)
            seen_ids.add(candidate["person_id"])
        else:
            rejected.append({"person_id": candidate.get("person_id") if isinstance(candidate, dict) else None,
                             "reasons": errors})
    results.sort(key=lambda c: (-c["score_total"], c.get("location_priority", 2),
                                c["person_name"].casefold()))
    selected = results[:target]
    return {"target": target, "considered": len(candidates), "passed_structural_gates": len(results),
            "contact_ready_pending_independent_evidence_audit": len(selected),
            "shortfall": max(0, target-len(selected)),
            "not_contact_ready": rejected, "candidates": selected,
            "messages_sent": 0, "verification_level": "STRUCTURAL_ONLY",
            "notice": "This is NOT a source-verified or independently qualified daily report."}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", required=True, help="Research-agent JSON array, private local path")
    ap.add_argument("--history", required=True, help="Private JSON list of historical stable person IDs")
    ap.add_argument("--output", required=True, help="Local report JSON path outside public Git")
    args = ap.parse_args()
    history_path = Path(args.history)
    if not history_path.is_file():
        raise SystemExit("BLOCKED: private historical identity file unavailable; cannot claim NEW")
    candidates = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    history = json.loads(history_path.read_text(encoding="utf-8"))
    if not isinstance(candidates, list) or not isinstance(history, list) or any(not isinstance(x, str) for x in history):
        raise SystemExit("BLOCKED: candidates must be a list and history must be an array of stable IDs")
    report = build_brief(candidates, set(history))
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k,v in report.items() if k not in ("candidates","not_contact_ready")}, indent=2))

if __name__ == "__main__":
    main()
