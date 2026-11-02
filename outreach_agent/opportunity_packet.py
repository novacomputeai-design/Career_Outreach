"""Strict public-only V1.1 organization-opportunity packet evaluation.

Does not use web, memory, emails, Google Drive or an automatic sender.
"""
import hashlib
import json
import re
from datetime import date
from pathlib import Path

from .opportunity_qualification import evaluate_opportunity, audit_opportunity_portfolio
from .project_scope import PROJECT_ID

MAX_BYTES = 131072
MAX_OPPORTUNITIES = 20
TOP = {"schema_version", "project_id", "run_id", "date_local", "opportunities"}


def build_opportunity_report(packet, *, pilot_size=5):
    if not isinstance(packet, dict) or set(packet) != TOP:
        raise ValueError("Exact V1.1 organization packet keys required")
    if packet["project_id"] != PROJECT_ID or packet["schema_version"] != "1.1":
        raise ValueError("Wrong personal career project or opportunity schema version")
    rid = packet["run_id"]
    if not isinstance(rid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,99}", rid):
        raise ValueError("Invalid run identifier")
    try:
        day = date.fromisoformat(packet["date_local"])
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid local date") from exc
    if day > date.today():
        raise ValueError("Cannot assess future dated research")
    opportunities = packet["opportunities"]
    if not isinstance(opportunities, list) or not 0 <= len(opportunities) <= MAX_OPPORTUNITIES:
        raise ValueError("Opportunity batch must contain 0..20 records")
    reports = [evaluate_opportunity(r) for r in opportunities]
    audit = audit_opportunity_portfolio(reports, pilot_size=pilot_size)
    return {
        "project_id": PROJECT_ID, "schema_version": "1.1",
        "run_id": rid, "date_local": day.isoformat(),
        "opportunities_researched": len(opportunities),
        "assessments": reports, "portfolio": audit,
        "private_history_checked": False, "independent_source_truth_verified": False,
        "new_contact_ready": 0, "messages_sent": 0,
        "warning": "Structural precheck only. No employment offer, verified vacancy, "
                   "contact readiness, new-person status or send authorization.",
    }


def assess_private_file(source, destination, *, pilot_size=5):
    root = Path(__file__).resolve().parents[1]
    source, destination = Path(source).resolve(), Path(destination).resolve()
    for path in (source, destination):
        if path == root or root in path.parents:
            raise ValueError("Research files must remain outside PUBLIC Git")
        if path.suffix.lower() != ".json":
            raise ValueError("Opportunity packets must be .json")
    if not source.is_file() or source.stat().st_size > MAX_BYTES:
        raise ValueError("Missing or oversized research input")
    if destination.exists():
        raise FileExistsError("No overwrite of existing opportunity report")
    if source == destination:
        raise ValueError("Source and report must be different")
    raw = source.read_bytes()
    packet = json.loads(raw.decode("utf-8-sig"))
    report = build_opportunity_report(packet, pilot_size=pilot_size)
    report["input_sha256"] = hashlib.sha256(raw).hexdigest()
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("x", encoding="utf-8") as stream:
        json.dump(report, stream, indent=2, ensure_ascii=False)
        stream.write("\n")
    return report
