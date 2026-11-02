"""DPAPI-owner-session-bound, append-only research preference journal.

This module does not authenticate a PERSON independently of their unlocked
Windows DPAPI keys. It does HMAC-bind every preference to an exact assessed
report, source receipt, opportunity identity and previous event across restarts.
No records grant contact, messaging, applications, scheduling or policy changes.
"""
from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import hmac
import json
import os
import re

from .career_source_witness import canonical, digest, verify_witness

DECISIONS = {"PURSUE", "RESEARCH_MORE", "REJECT"}
REASONS = {
    "LEADERSHIP_SCOPE", "NO_MEANINGFUL_CONTRIBUTION", "DOMAIN_FIT",
    "EMPLOYMENT_PATH", "TIMING_NOT_COMPELLING", "EXISTING_OWNER_OVERLAP",
    "CONTACT_ACCESS", "SOURCE_GAP", "ROLE_MATCH", "TUCSON_LOCATION", "OTHER",
}
CONTEXT = b"CAREER_OWNER_V22_RESEARCH_REVIEW_EVENT\0"
GENESIS = "0" * 64
ROOT = Path(__file__).resolve().parents[1]


def _private_folder(folder):
    path = Path(folder).expanduser().resolve()
    if path == ROOT or ROOT in path.parents:
        raise ValueError("PRIVATE_OWNER_JOURNAL_OUTSIDE_PUBLIC_GIT_REQUIRED")
    if path.is_symlink():
        raise ValueError("JOURNAL_SYMLINK_REJECTED")
    return path


def _signed(event, key):
    unsigned = dict(event)
    unsigned.pop("mac", None)
    return hmac.new(key, CONTEXT + canonical(unsigned), hashlib.sha256).hexdigest()


def _read_verified(journal, key):
    if not journal.exists():
        return []
    if journal.is_symlink() or journal.stat().st_size > 1024 * 1024:
        raise ValueError("JOURNAL_INVALID_OR_TOO_LARGE")
    output, last = [], GENESIS
    for line in journal.read_text(encoding="utf-8").splitlines():
        event = json.loads(line)
        if (event.get("sequence") != len(output) + 1
                or event.get("previous_mac") != last
                or not isinstance(event.get("mac"), str)
                or not hmac.compare_digest(event["mac"], _signed(event, key))):
            raise ValueError("OWNER_DECISION_JOURNAL_INTEGRITY_FAILURE")
        if (event.get("contact_ready") is not False
                or event.get("send_authorized") is not False
                or event.get("application_submitted") is not False):
            raise ValueError("OWNER_JOURNAL_ACTION_AUTHORITY_FORBIDDEN")
        last = event["mac"]
        output.append(event)
    return output


def verify_owner_journal(folder, secret):
    if not isinstance(secret, (bytes, bytearray)) or len(secret) < 32:
        raise ValueError("OWNER_PRIVATE_KEY_REQUIRED")
    journal = _private_folder(folder) / "owner-reviews.jsonl"
    events = _read_verified(journal, secret)
    return {"verified_events": len(events), "chain_head": events[-1]["mac"] if events else GENESIS,
            "owner_identity_independently_authenticated": False,
            "assurance": "OWNER_DPAPI_KEY_BOUND_JOURNAL_NOT_HARDWARE_IDENTITY",
            "send_authorized": False}


def validate_owner_handoff(report, witness, secret, index):
    if (not isinstance(report, dict) or report.get("schema_version") != "2.2"
            or report.get("contact_ready") != 0 or report.get("send_authorized") is not False
            or report.get("native_skills_verified") is not False
            or report.get("source_truth_independently_verified") is not False):
        raise ValueError("UNTRUSTED_RESEARCH_REPORT")
    records, assessments = report.get("opportunity_records"), report.get("assessments")
    if (not isinstance(records, list) or not isinstance(assessments, list)
            or len(records) != len(assessments)
            or not isinstance(index, int) or not 0 <= index < len(records)):
        raise ValueError("INVALID_RESEARCH_OPPORTUNITY_SELECTION")
    packet = {"schema_version": "2.2", "project_id": report["project_id"],
              "run_id": report["run_id"], "date_local": report["date_local"],
              "opportunities": records}
    from .career_contribution import validate_v22_packet
    from scripts.assess_career_opportunities_v22 import assess_v22_packet
    validate_v22_packet(packet)
    recomputed = assess_v22_packet(packet)
    if canonical(recomputed["assessments"]) != canonical(assessments):
        raise ValueError("ASSESSMENT_TAMPER_OR_EVALUATOR_VERSION_MISMATCH")
    if not verify_witness(witness, packet, secret):
        raise ValueError("SOURCE_WITNESS_BINDING_INVALID")
    observed = witness.get("results")
    expected = [(i, c["claim_id"], c["source_url"])
                for i, item in enumerate(records) for c in item["claims"]]
    if (not isinstance(observed, list) or len(observed) != len(expected)
            or any((row.get("index"), row.get("claim_id"), row.get("url")) != match
                   or row.get("status") not in {
                       "TEXT_REPRODUCED","TEXT_NOT_FOUND",
                       "FETCH_UNAVAILABLE","HOST_NOT_APPROVED"}
                   for row, match in zip(observed, expected))):
        raise ValueError("SOURCE_WITNESS_CLAIM_COVERAGE_INVALID")
    if witness.get("all_source_text_reproduced") is not (
            bool(observed) and all(row["status"] == "TEXT_REPRODUCED" for row in observed)):
        raise ValueError("SOURCE_WITNESS_AGGREGATE_MISMATCH")
    assessment = assessments[index]
    if (assessment.get("contact_ready") is not False
            or assessment.get("send_authorized") is not False
            or assessment.get("application_submitted") is not False):
        raise ValueError("UNAUTHORIZED_RESEARCH_ACTION_STATE")
    return records[index], assessment, digest(report), digest(witness)


def append_owner_preference(folder, secret, *, report, witness, index, decision,
                            reason, memory_result, consent):
    """Append exactly one consented RESEARCH preference, never contact approval."""
    if decision not in DECISIONS or reason not in REASONS:
        raise ValueError("INVALID_OWNER_DECISION_OR_REASON")
    record, result, report_hash, witness_hash = validate_owner_handoff(
        report, witness, secret, index)
    if consent is not True:
        raise ValueError("EXPLICIT_INTERACTIVE_OWNER_CONSENT_REQUIRED")
    if not isinstance(memory_result, dict):
        raise ValueError("OWNER_PRIVATE_MEMORY_SCREENING_REQUIRED")
    classification = memory_result.get("result")
    if classification not in {
        "EXISTING_RELATIONSHIP", "SEEN_IN_STORE", "NOT_FOUND_IN_LOCAL_STORE",
        "DUPLICATE_IN_BATCH_HOLD", "AMBIGUOUS_IDENTITY_HOLD",
        "IDENTITY_CONFLICT_HOLD", "POSSIBLE_NAMESAKE_HOLD", "NO_NAMED_EXECUTIVE",
    }:
        raise ValueError("INVALID_PRIVATE_HISTORY_CLASSIFICATION")
    if (record.get("executive") is None) != (classification == "NO_NAMED_EXECUTIVE"):
        raise ValueError("PRIVATE_HISTORY_PERSON_BINDING_MISMATCH")
    base = _private_folder(folder)
    base.mkdir(parents=True, exist_ok=True)
    journal, lock = base / "owner-reviews.jsonl", base / "owner-reviews.lock"
    # A lock file is created exclusively and held until the append fsyncs.
    # A crashed stale lock requires explicit operator investigation, not force unlock.
    with lock.open("x", encoding="utf-8") as stream:
        stream.write(str(os.getpid()))
    try:
        history = _read_verified(journal, secret)
        identity = json.dumps(result.get("opportunity_identity"), separators=(",", ":"))
        if identity == "null":
            raise ValueError("UNRESOLVED_OPPORTUNITY_IDENTITY")
        if any(row["report_sha256"] == report_hash and
               row["opportunity_identity"] == identity for row in history):
            raise ValueError("OWNER_DECISION_REPLAY_OR_DUPLICATE_REVIEW")
        event = {
            "version": "1.0", "sequence": len(history) + 1,
            "previous_mac": history[-1]["mac"] if history else GENESIS,
            "occurred_at_utc": datetime.now(timezone.utc).isoformat(),
            "project_id": "PERSONAL_CAREER_OUTREACH",
            "run_id": report["run_id"],
            "report_sha256": report_hash, "witness_sha256": witness_hash,
            "opportunity_identity": identity, "decision": decision, "reason": reason,
            "capability_theme": record["capability_theme"],
            "engagement_pathway": record["engagement_pathway"],
            "local_memory_classification": classification,
            "cross_channel_novelty_verified": False,
            "owner_session": "DPAPI_KEY_BOUND_OPERATOR_PROMPT_NOT_INDEPENDENT_PERSON_ID",
            "contact_ready": False, "send_authorized": False,
            "application_submitted": False,
        }
        event["mac"] = _signed(event, secret)
        with journal.open("a", encoding="utf-8", newline="\n") as dest:
            dest.write(json.dumps(event, sort_keys=True, ensure_ascii=False) + "\n")
            dest.flush()
            os.fsync(dest.fileno())
        return {
            "decision_recorded": decision, "reason": reason, "sequence": event["sequence"],
            "chain_mac": event["mac"], "source_text_all_reproduced":
                witness.get("all_source_text_reproduced") is True,
            "independent_human_identity_proven": False, "contact_ready": False,
            "send_authorized": False, "application_submitted": False,
        }
    finally:
        lock.unlink(missing_ok=True)


def propose_verified_owner_learning(folder, secret):
    """Advisory proposals from HMAC-verified owner events, never auto-applied."""
    from .career_owner_learning import propose_career_discovery_improvements
    history = _read_verified(_private_folder(folder) / "owner-reviews.jsonl", secret)
    latest = {}
    for event in history:
        if ("capability_theme" not in event or "engagement_pathway" not in event):
            raise ValueError("OWNER_FEEDBACK_VERSION_OR_FIELDS_NOT_SUPPORTED")
        latest[event["opportunity_identity"]] = {
            "opportunity_identity": event["opportunity_identity"],
            "decision": event["decision"], "reason": event["reason"],
            "capability_theme": event["capability_theme"],
            "engagement_pathway": event["engagement_pathway"],
        }
    result = propose_career_discovery_improvements(list(latest.values()))
    result["input_journal_mac_verified"] = True
    result["owner_identity_independently_authenticated"] = False
    result["policy_modified"] = False
    result["send_authorized"] = False
    return result
