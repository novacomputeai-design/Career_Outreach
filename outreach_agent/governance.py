"""Deterministic operator-review and approval preconditions.

These structural guards DO NOT authenticate operator identity or independently verify
web source truth. They fail closed and record policy version; no sending permitted.
"""
from __future__ import annotations
import json
from pathlib import Path

POLICY_PATH = Path(__file__).resolve().parents[1] / "config" / "operating-policy.json"

def active_policy() -> dict:
    policy = json.loads(POLICY_PATH.read_text(encoding="utf-8"))
    governance = policy.get("governance", {})
    outreach = policy.get("outreach", {})
    if (
        not isinstance(policy.get("version"), str)
        or outreach.get("automatic_sending") is not False
        or outreach.get("individual_draft_approval") is not True
        or outreach.get("separate_send_authorization") is not True
        or governance.get("automatic_sending_prohibited") is not True
        or governance.get("contact_ready_requires_independent_human_review") is not True
        or governance.get("no_model_self_approval") is not True
        or governance.get("draft_authorization_bound_to_content_hash") is not True
    ):
        raise RuntimeError("Required governance controls missing/disabled; fail closed")
    return policy

def structural_review_gate(record: dict, *, opted_out: bool, policy: dict | None = None) -> dict:
    """Return deterministic HOLD or PENDING_HUMAN_REVIEW, not independently verified PASS."""
    policy = policy or active_policy()
    reasons = []
    if opted_out:
        reasons.append("SUPPRESSED_IDENTITY")
    if record.get("user_relationship_status") == "PREVIOUSLY_MET":
        # Existing relationships can be relevant to follow-up, but not claimed NEW.
        reasons.append("EXISTING_RELATIONSHIP_NOT_NEW")
    # The old researcher has a strict pre-report structural audit, including
    # schema, score, quote and two-source host checks. No source truth claim.
    from .pipeline import audit_record
    if not audit_record(record):
        reasons.append("INSUFFICIENT_SOURCE_ROUTE_OR_SCORE_EVIDENCE")
    if record.get("score_total", 0) < policy["minimum_qualification_score"]:
        reasons.append("BELOW_POLICY_SCORE")
    # Operator-reported FIRST_LEARNED is not source evidence or a clearance.
    return {
        "policy_version": policy["version"],
        "decision": "HOLD" if reasons else "PENDING_HUMAN_REVIEW",
        "reasons": sorted(set(reasons)),
        "assurance": "DETERMINISTIC_STRUCTURAL_PRECHECK_ONLY",
        "contact_ready": False,
    }

def approval_gate(structural: dict, *, user_review_recorded: bool, stage: str,
                  draft_content_preapproved: bool = False) -> dict:
    """No approval unless human review is recorded; sending still disabled."""
    reasons = list(structural["reasons"])
    if structural["decision"] != "PENDING_HUMAN_REVIEW":
        reasons.append("STRUCTURAL_GATE_NOT_PASSED")
    if not user_review_recorded:
        reasons.append("INDEPENDENT_REVIEW_NOT_RECORDED")
    if stage not in ("CONTENT_APPROVED", "SEND_AUTHORIZED"):
        reasons.append("INVALID_APPROVAL_STAGE")
    if stage == "SEND_AUTHORIZED" and not draft_content_preapproved:
        reasons.append("EXACT_DRAFT_CONTENT_NOT_APPROVED")
    return {
        "policy_version": structural["policy_version"],
        "decision": "HOLD" if reasons else "ALLOW_APPROVAL_RECORD",
        "reasons": sorted(set(reasons)),
        "assurance": "LOCAL_OPERATOR_ATTESTATION_ONLY",
        "outbound_sent": False,
    }
