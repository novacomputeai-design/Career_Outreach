"""Immutable, public-research-only opportunity snapshots in a user-owned directory.

Not a relationship store, owner-approval database, authenticated audit trail,
live source-verification service or authorization to contact anyone. Never write
inside the public checkout. A missing opportunity is NOT a closed job.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date
from pathlib import Path
import json
import re

from .career_intelligence import opportunity_identity

_RUN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{2,99}$")
_REPO = Path(__file__).resolve().parents[1]


def _root(path):
    root = Path(path).expanduser().resolve()
    if root == _REPO or _REPO in root.parents:
        raise ValueError("PRIVATE_RUN_FOLDER_MUST_BE_OUTSIDE_PUBLIC_REPOSITORY")
    if root.exists() and not root.is_dir():
        raise ValueError("RUN_HISTORY_NOT_A_DIRECTORY")
    return root


def _identity(record):
    projected = deepcopy(record)
    if projected.get("schema_version") == "2.2":
        projected["schema_version"] = "2.1"
        projected.pop("career_value", None)
    key, error = opportunity_identity(projected)
    if error or not key:
        raise ValueError("OPPORTUNITY_IDENTITY_UNRESOLVED")
    # JSON array is the canonical serialized tuple; requisition strings remain intact.
    return json.dumps(key, separators=(",", ":"), ensure_ascii=False)


def _read_snapshots(folder):
    if not folder.exists():
        return []
    found = []
    for path in sorted(folder.glob("*.json")):
        if path.is_symlink():
            raise ValueError("SYMLINK_RUN_SNAPSHOT_REJECTED")
        obj = json.loads(path.read_text(encoding="utf-8"))
        if obj.get("kind") != "PUBLIC_ONLY_CAREER_RESEARCH_SNAPSHOT":
            raise ValueError("UNRECOGNIZED_RUN_SNAPSHOT")
        found.append(obj)
    return found


def build_reconciliation(prior, *, run_id, date_local, opportunity_records, assessments):
    """Pure reconciliation; never hides a previously observed identity."""
    if not _RUN.fullmatch(run_id):
        raise ValueError("INVALID_RUN_ID")
    date.fromisoformat(date_local)
    if len(opportunity_records) != len(assessments):
        raise ValueError("RUN_RECORD_ASSESSMENT_COUNT_MISMATCH")
    history = {}
    for snapshot in prior:
        for item in snapshot["observations"]:
            key = item["identity_key"]
            original = history.get(key, {})
            history[key] = {
                "identity_key": key,
                "first_seen_run": original.get("first_seen_run", snapshot["run_id"]),
                "last_seen_run": snapshot["run_id"],
                "last_observed_state": item["research_state"],
            }
    current = {}
    for record, assessment in zip(opportunity_records, assessments):
        identity = _identity(record)
        if identity in current:
            raise ValueError("DUPLICATE_OPPORTUNITY_IDENTITY_IN_RUN")
        if assessment.get("owner_decision") not in ("NOT_REVIEWED", None):
            raise ValueError("UNAUTHENTICATED_OWNER_DECISION_IN_RESEARCH_PACKET")
        if assessment.get("send_authorized") is not False or assessment.get("contact_ready") is not False:
            raise ValueError("RESEARCH_CANNOT_GRANT_ENGAGEMENT_PERMISSION")
        current[identity] = {
            "identity_key": identity,
            "research_state": assessment["research_state"],
            "engagement_readiness": assessment["engagement_readiness"],
        }
    continuity = []
    for key in sorted(set(history) | set(current)):
        h = history.get(key)
        now = current.get(key)
        continuity.append({
            "identity_key": key,
            "first_seen_run": h["first_seen_run"] if h else run_id,
            "last_seen_run": run_id if now else h["last_seen_run"],
            "current_run_observation": "OBSERVED" if now else "NOT_OBSERVED_THIS_RUN",
            "current_research_state": now["research_state"] if now else None,
            "last_observed_state": now["research_state"] if now else h["last_observed_state"],
            "actionable_now": False,
        })
    return {
        "kind": "PUBLIC_ONLY_CAREER_RESEARCH_SNAPSHOT", "version": "1.0",
        "run_id": run_id, "date_local": date_local,
        "observations": [current[k] for k in sorted(current)],
        "continuity": continuity,
        "source_truth_independently_verified": False,
        "native_execution_independently_verified": False,
        "owner_approval_authenticated": False,
        "contact_ready": False, "send_authorized": False,
        "notes": "Missing from a new run never means withdrawn, closed, rejected, or forgotten.",
    }


def record_run_snapshot(private_history_dir, *, run_id, date_local,
                        opportunity_records, assessments):
    """Create once, fail closed on conflicting replays. Never overwrite older runs."""
    root = _root(private_history_dir)
    run_folder = root / "runs"
    if run_folder.is_symlink():
        raise ValueError("SYMLINK_HISTORY_DIR_REJECTED")
    prior = _read_snapshots(run_folder)
    snapshot = build_reconciliation(prior, run_id=run_id, date_local=date_local,
                                    opportunity_records=opportunity_records,
                                    assessments=assessments)
    payload = json.dumps(snapshot, sort_keys=True, ensure_ascii=False, indent=2) + "\n"
    outfile = run_folder / (run_id + ".json")
    if outfile.exists():
        if outfile.read_text(encoding="utf-8") == payload:
            return snapshot
        raise FileExistsError("RUN_ID_REUSED_WITH_DIFFERENT_CONTENT")
    run_folder.mkdir(parents=True, exist_ok=True)
    with outfile.open("x", encoding="utf-8") as stream:
        stream.write(payload)
    return snapshot


def read_latest_continuity(private_history_dir):
    prior = _read_snapshots(_root(private_history_dir) / "runs")
    if not prior:
        return []
    return prior[-1]["continuity"]
