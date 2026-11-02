"""Structural skill activation plan/audit only; cannot prove Codex native invocation."""
from __future__ import annotations

ALL = {
    "daily-executive-outreach", "organization-discovery", "leadership-discovery",
    "contact-verification", "provenance-and-freshness", "relationship-memory",
    "relationship-qualification", "outreach-drafting", "conversation-preparation",
    "follow-up-planning", "run-quality-audit", "daily-executive-brief",
    "outcome-intelligence", "discovery-strategy-optimization",
}
ALWAYS = {
    "daily-executive-outreach", "organization-discovery", "provenance-and-freshness",
    "relationship-qualification", "run-quality-audit", "daily-executive-brief",
}
STATE = {"HOST_REPORTED_NATIVE", "NOT_VERIFIED", "SKIPPED_NOT_APPLICABLE"}


def required_skills(*, named_executive=False, person_contact_review=False,
                    draft_requested=False, planned_meeting=False,
                    existing_followup=False, feedback_or_outcomes=False):
    required = set(ALWAYS)
    if named_executive:
        required.update({"leadership-discovery", "contact-verification"})
    if person_contact_review:
        required.add("relationship-memory")
    if draft_requested:
        required.add("outreach-drafting")
    if planned_meeting:
        required.add("conversation-preparation")
    if existing_followup:
        required.add("follow-up-planning")
    if feedback_or_outcomes:
        required.update({"outcome-intelligence", "discovery-strategy-optimization"})
    return required


def audit_skill_trace(records, **case):
    """Structural audit; actual native invocation requires independent host transcript."""
    required = required_skills(**case)
    invalid = []
    missing = sorted(required.difference(records))
    for skill, observation in records.items():
        if skill not in ALL or not isinstance(observation, dict):
            invalid.append(skill)
            continue
        state = observation.get("state")
        if state not in STATE:
            invalid.append(skill)
        elif state == "SKIPPED_NOT_APPLICABLE":
            if skill in required or not observation.get("reason"):
                invalid.append(skill)
        elif state == "HOST_REPORTED_NATIVE" and not observation.get("activation_evidence"):
            invalid.append(skill)
    return {"required": sorted(required), "missing": missing,
            "invalid": sorted(set(invalid)), "all_skills_covered": len(records) == len(ALL),
            "structural_pass": not invalid and not missing,
            "independent_native_execution_verified": False,
            "assurance": "STRUCTURAL_TRACE_ONLY_REQUIRES_ACTUAL_HOST_EVIDENCE"}
