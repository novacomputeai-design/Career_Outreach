"""V2.2 contribution and timing preflight.

These checks validate STRUCTURE and linkage to source-claimed records. They do not
browse, establish source truth, authenticate an owner, or authorize engagement.
Only an explicit, independent source/owner review can promote a field hypothesis.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path
import json

from jsonschema import Draft202012Validator, FormatChecker

from .career_intelligence import _claim, evaluate_opportunity

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "schemas" / "career-opportunity-v2.2.schema.json"

# Stable, conservative references drawn from config/public-candidate-profile.md.
# These are source-reference identifiers, not assertions of clinical or utility expertise.
PUBLIC_CANDIDATE_CAPABILITIES = frozenset({
    "MOBIUS_PRODUCT_PORTFOLIO", "MOBIUS_AI_PRIORITIZATION",
    "MOBIUS_PRODUCT_TEAM_LEADERSHIP", "UCHICAGO_PLATFORM_MODERNIZATION",
    "WELLS_FARGO_REGULATED_OPERATIONS",
})


def validate_v22_packet(packet):
    """Strict versioned schema: rejects incomplete nested claims and unsupported keys."""
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(packet),
                    key=lambda e: tuple(str(x) for x in e.absolute_path))
    if errors:
        first = errors[0]
        where = ".".join(map(str, first.absolute_path)) or "packet"
        raise ValueError("V2.2_SCHEMA_INVALID at " + where + ": " + first.message)


def assess_contribution(record):
    """Evaluate a bounded *hypothesis*, not the need for a new job."""
    value = record["career_value"]
    org = record["organization"]
    claims = {c["claim_id"]: c for c in record["claims"]}
    reasons = []
    candidate_refs = value["candidate_evidence_refs"]
    if not candidate_refs or not set(candidate_refs) <= PUBLIC_CANDIDATE_CAPABILITIES:
        reasons.append("CANDIDATE_CAPABILITY_EVIDENCE_UNKNOWN")
    if value["existing_owner_status"] == "OWNER_UNKNOWN":
        reasons.append("EXISTING_PRODUCT_LEADERSHIP_UNKNOWN")
    # An existing executive may make a complementary remit sensible; there
    # must still be an explicit owner review, not an invented vacancy.
    if value["existing_owner_status"] == "EXISTING_OWNER_DOCUMENTED":
        reasons.append("EXISTING_OWNER_REMIT_REQUIRES_COMPARATIVE_REVIEW")
    if value["maturity"] == "UNKNOWN":
        reasons.append("INITIATIVE_MATURITY_UNVERIFIED")

    objective_id = record["initiative"].get("objective_claim_id")
    if record["engagement_pathway"] == "STRATEGIC_EXPLORATION":
        if not _claim(claims, objective_id, kind="BUSINESS_OBJECTIVE",
                      subject=org["organization_id"]):
            reasons.append("BUSINESS_OBJECTIVE_SOURCE_UNVERIFIED")

    trigger = _claim(claims, value["trigger_claim_id"], kind="BUSINESS_TRIGGER",
                     subject=org["organization_id"]) if value["trigger_claim_id"] else None
    if not trigger:
        timing = "NO_TIMING_BASIS"
        reasons.append("NO_VERIFIED_BUSINESS_TRIGGER")
    else:
        published = trigger.get("published_on")
        try:
            day = date.fromisoformat(published)
        except (TypeError, ValueError):
            day = None
        if day and date.today() - timedelta(days=180) <= day <= date.today():
            timing = "RESEARCH_NOW"
        else:
            timing = "MONITOR_TRIGGER"
            reasons.append("BUSINESS_TRIGGER_STALE_OR_UNDATED")
    # Even a structurally strong claim is a source-reported hypothesis.
    if "BUSINESS_OBJECTIVE_SOURCE_UNVERIFIED" in reasons or "CANDIDATE_CAPABILITY_EVIDENCE_UNKNOWN" in reasons:
        quality = "NO_CREDIBLE_CONTRIBUTION"
    elif (value["existing_owner_status"] == "OWNER_UNKNOWN"
          or value["maturity"] == "UNKNOWN"):
        quality = "CONTRIBUTION_RESEARCH_NEEDED"
    else:
        quality = "STRONG_CONTRIBUTION"
    return {
        "contribution_quality": quality,
        "timing_status": timing,
        "reason_codes": sorted(set(reasons)),
        "proposed_internal_responsibility": value["proposed_internal_responsibility"],
        "candidate_capability_refs": list(candidate_refs),
        "existing_owner_status": value["existing_owner_status"],
        "source_assurance": "SELF_REPORTED_SOURCE_METADATA_NOT_INDEPENDENTLY_VERIFIED",
        "leadership_gap_or_hiring_proven": False,
    }


def evaluate_v22_opportunity(record):
    """Reuse proven V2.1 safety gates; V2.2 only adds constraints or holds."""
    if record.get("schema_version") != "2.2":
        raise ValueError("V2.2_REQUIRED")
    projected = deepcopy(record)
    projected["schema_version"] = "2.1"
    projected.pop("career_value")
    baseline = evaluate_opportunity(projected)
    quality = assess_contribution(record)
    baseline["schema_version"] = "2.2"
    baseline["career_value_assessment"] = quality
    if record["engagement_pathway"] == "STRATEGIC_EXPLORATION":
        if quality["contribution_quality"] == "NO_CREDIBLE_CONTRIBUTION":
            baseline["research_state"] = "EVIDENCE_HOLD"
            baseline["engagement_readiness"] = "NOT_PREPARED"
            baseline["reasons"] = sorted(set(baseline["reasons"] + ["NO_CREDIBLE_CONTRIBUTION"]))
        elif quality["contribution_quality"] == "CONTRIBUTION_RESEARCH_NEEDED":
            if baseline["engagement_readiness"] == "ENGAGEMENT_REVIEW_ELIGIBLE":
                baseline["engagement_readiness"] = "RESEARCH_PENDING"
            baseline["reasons"] = sorted(set(baseline["reasons"] + ["CONTRIBUTION_RESEARCH_NEEDED"]))
    # A source-reported quality result NEVER grants permission to contact or apply.
    if baseline["engagement_readiness"] == "ENGAGEMENT_REVIEW_ELIGIBLE":
        baseline["engagement_readiness"] = "RESEARCH_PENDING"
        baseline["reasons"] = sorted(set(baseline["reasons"] + ["INDEPENDENT_SOURCE_REVIEW_PENDING"]))
    baseline["contact_ready"] = False
    baseline["send_authorized"] = False
    baseline["application_submitted"] = False
    baseline["source_truth_independently_verified"] = False
    return baseline
