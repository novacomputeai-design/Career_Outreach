"""Strict, non-authoritative audit of a Codex-to-evaluator research handoff.

This checks stage order and declared SHA-256 artifact binding but cannot certify
a Codex native invocation or that source content actually came from the web.
"""
from __future__ import annotations

import re

STAGES = (
    "organization_discovery", "provenance_review",
    "contribution_and_timing", "executive_responsibility",
    "person_access", "offline_evaluator", "owner_brief",
)
STATES = {"REPORTED_COMPLETED", "NOT_VERIFIED", "SKIPPED_NOT_APPLICABLE"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")


def audit_research_handoffs(records):
    if not isinstance(records, list) or len(records) != len(STAGES):
        raise ValueError("V22_HANDOFF_STAGE_COUNT_MISMATCH")
    names = [x.get("stage") if isinstance(x, dict) else None for x in records]
    if tuple(names) != STAGES:
        raise ValueError("V22_HANDOFF_STAGE_ORDER_INVALID")
    problems = []
    previous = None
    for row in records:
        name = row["stage"]
        state = row.get("state")
        if state not in STATES:
            raise ValueError("V22_HANDOFF_STAGE_STATE_INVALID")
        input_hash = row.get("input_digest")
        output_hash = row.get("output_digest")
        if state == "REPORTED_COMPLETED":
            if not (isinstance(input_hash, str) and SHA256.fullmatch(input_hash)
                    and isinstance(output_hash, str) and SHA256.fullmatch(output_hash)):
                problems.append(name + ":MISSING_ARTIFACT_DIGEST")
            if previous is not None and previous != input_hash:
                problems.append(name + ":BROKEN_STAGE_HANDOFF")
        elif state == "SKIPPED_NOT_APPLICABLE":
            if name in ("organization_discovery","provenance_review",
                        "contribution_and_timing","offline_evaluator","owner_brief"):
                problems.append(name + ":REQUIRED_STAGE_SKIPPED")
            if not row.get("reason"):
                problems.append(name + ":SKIP_REASON_MISSING")
            if previous is not None and input_hash != previous:
                problems.append(name + ":SKIP_INPUT_BINDING_MISMATCH")
            if input_hash != output_hash:
                problems.append(name + ":SKIP_MUST_FORWARD_INPUT_UNCHANGED")
        else:
            problems.append(name + ":STAGE_NOT_VERIFIED")
        if state in ("REPORTED_COMPLETED","SKIPPED_NOT_APPLICABLE"):
            previous = output_hash
        else:
            previous = None
    return {
        "stage_count": len(records), "required_stage_names": list(STAGES),
        "structural_handoff_complete": not problems,
        "problems": sorted(set(problems)),
        "native_codex_invocation_verified": False,
        "source_truth_independently_verified": False,
        "private_history_authenticated": False,
        "contact_ready": False,
        "send_authorized": False,
        "assurance": "SELF_REPORTED_DIGEST_CHAIN_NOT_A_HOST_TRUST_ANCHOR",
    }
