"""Owner-reviewed bridge between public research and private history classifications.

This is deliberately NOT a Codex-to-DPAPI broker. It uses an operator-supplied,
read-minimized batch response. Neither a local absence nor this handoff grants
new-contact readiness, human approval, or sending permission.
"""
from __future__ import annotations

from .memory_batch import candidate_input_fingerprint
from .project_scope import PROJECT_ID, scope_reasons
from .state import normalized

KNOWN_RESULTS = {
    "EXISTING_RELATIONSHIP": "EXISTING_FOLLOW_UP_NOT_NEW",
    "SEEN_IN_STORE": "ALREADY_DISCOVERED_NOT_NEW",
    "NOT_FOUND_IN_LOCAL_STORE": "NOVELTY_UNVERIFIED_HOLD",
    "DUPLICATE_IN_BATCH_HOLD": "IDENTITY_HOLD",
    "AMBIGUOUS_IDENTITY_HOLD": "IDENTITY_HOLD",
    "IDENTITY_CONFLICT_HOLD": "IDENTITY_HOLD",
    "POSSIBLE_NAMESAKE_HOLD": "IDENTITY_HOLD",
}
EXPECTED_NOVELTY = {
    "EXISTING_RELATIONSHIP": "ALREADY_IN_LOCAL_STORE",
    "SEEN_IN_STORE": "ALREADY_IN_LOCAL_STORE",
    "NOT_FOUND_IN_LOCAL_STORE": "UNVERIFIED",
    "DUPLICATE_IN_BATCH_HOLD": "UNVERIFIED",
    "AMBIGUOUS_IDENTITY_HOLD": "UNVERIFIED",
    "IDENTITY_CONFLICT_HOLD": "UNVERIFIED",
    "POSSIBLE_NAMESAKE_HOLD": "UNVERIFIED",
}


def reconcile_operator_screening(candidates: list, screening: dict) -> dict:
    """Fail closed on any mismatch; return minimal classifications, no drafts."""
    if not isinstance(candidates, list) or not 1 <= len(candidates) <= 100:
        raise ValueError("Expected 1..100 public personal-career candidates")
    if not isinstance(screening, dict):
        raise ValueError("Operator screening result must be an object")
    if (screening.get("verification_level") != "OPERATOR_PROTECTED_LOCAL_STORE_ONLY"
            or screening.get("complete_cross_channel_history_verified") is not False
            or screening.get("new_contact_ready_granted") != 0):
        raise ValueError("Untrusted or overstated screening assurance")
    records = []
    indexed = set()
    for item in candidates:
        if not isinstance(item, dict) or scope_reasons(item, require_project_id=True):
            raise ValueError("Personal career candidate identity/purpose failed scope gate")
        name = item.get("person_name")
        profile = item.get("profile_url")
        if not isinstance(name, str) or len(name.strip().split()) < 2:
            raise ValueError("Candidate requires a complete name")
        if profile is not None and not isinstance(profile, str):
            raise ValueError("Malformed individual profile URL")
        name = " ".join(name.strip().split())
        identity = normalized(name)
        if identity in indexed:
            raise ValueError("Duplicate names require human identity resolution")
        indexed.add(identity)
        records.append((name, profile or None))
    expected_fingerprint = candidate_input_fingerprint(records)
    if screening.get("input_fingerprint") != expected_fingerprint:
        raise ValueError("Screening does not match ordered candidate names and profiles")
    results = screening.get("results")
    if (screening.get("people_checked") != len(records)
            or not isinstance(results, list) or len(results) != len(records)):
        raise ValueError("Incomplete or inconsistent screening batch")
    output = []
    for (name, _), row in zip(records, results):
        if not isinstance(row, dict) or normalized(row.get("person_name")) != normalized(name):
            raise ValueError("Screening row/name binding mismatch")
        status = row.get("result")
        if status not in KNOWN_RESULTS or row.get("novelty") != EXPECTED_NOVELTY[status]:
            raise ValueError("Unsupported identity/novelty classification")
        if row.get("granted_contact_readiness") is not False:
            raise ValueError("Screening must not confer contact-readiness")
        suppressed = row.get("suppressed")
        if suppressed is not None and not isinstance(suppressed, bool):
            raise ValueError("Invalid suppression state")
        classification = ("SUPPRESSED_HOLD" if suppressed is True
                          else KNOWN_RESULTS[status])
        output.append({
            "person_name": name,
            "local_classification": status,
            "operator_review_queue": classification,
            "novelty": row["novelty"],
            "contact_ready": False,
        })
    return {
        "project_id": PROJECT_ID,
        "verification_level": "OPERATOR_SUPPLIED_LOCAL_CLASSIFICATION_ONLY",
        "operator_identity_authenticated": False,
        "complete_cross_channel_history_verified": False,
        "new_contact_ready": 0,
        "send_authorized": False,
        "people_reconciled": len(output),
        "classifications": output,
        "warning": (
            "Operator-supplied file is not signed or independently authenticated; "
            "NOT_FOUND_IN_LOCAL_STORE never establishes a new contact. "
            "Review aliases, outside history, source truth and recipient route separately."
        ),
    }
