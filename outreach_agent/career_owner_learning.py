"""Advisory-only analysis of operator-supplied career opportunity feedback.

This does NOT authenticate the operator or persist private events. The caller
must keep raw decisions in an owner-controlled protected store. No weights,
policy, queries, outreach or approvals are modified by this module.
"""
from collections import Counter

VALID_DECISIONS = {"PURSUE", "RESEARCH_MORE", "REJECT"}
VALID_REASONS = {
    "TUCSON_LOCATION", "NO_MEANINGFUL_CONTRIBUTION", "LEADERSHIP_SCOPE",
    "ROLE_MATCH", "EMPLOYMENT_PATH", "CONTACT_ACCESS", "DOMAIN_FIT",
    "SOURCE_GAP", "TIMING_NOT_COMPELLING", "EXISTING_OWNER_OVERLAP", "OTHER",
}
VALID_THEMES = {"AI_STRATEGY_TRANSFORMATION", "ENTERPRISE_PRODUCT_LEADERSHIP", "BOTH"}
VALID_PATHWAYS = {"STRATEGIC_EXPLORATION", "DIRECT_HIRING"}


def propose_career_discovery_improvements(events, *, minimum_reviews=6):
    """Explain repeat dissatisfaction without self-changing any search policy."""
    if not isinstance(events, list):
        raise ValueError("REVIEW_EVENTS_MUST_BE_LIST")
    unique = {}
    for event in events:
        if not isinstance(event, dict):
            raise ValueError("INVALID_OWNER_REVIEW_EVENT")
        key = event.get("opportunity_identity")
        decision = event.get("decision")
        reason = event.get("reason")
        if (not isinstance(key, str) or not key
                or decision not in VALID_DECISIONS
                or reason not in VALID_REASONS
                or event.get("capability_theme") not in VALID_THEMES
                or event.get("engagement_pathway") not in VALID_PATHWAYS):
            raise ValueError("INVALID_OWNER_REVIEW_EVENT")
        # Latest event order may be known to the owner-private system; the
        # analytic receives one current event per opportunity, not an auth log.
        if key in unique:
            raise ValueError("DUPLICATE_OPPORTUNITY_REVIEW_REQUIRES_OWNER_RECONCILIATION")
        unique[key] = event
    verdicts = Counter(x["decision"] for x in unique.values())
    rejects = Counter(x["reason"] for x in unique.values() if x["decision"] == "REJECT")
    if len(unique) < minimum_reviews:
        return {
            "status": "INSUFFICIENT_OWNER_REVIEWS", "reviewed": len(unique),
            "by_decision": dict(verdicts), "proposals": [],
            "auto_applied": False, "policy_modified": False,
            "source_assurance": "OPERATOR_SUPPLIED_FEEDBACK_NOT_AUTHENTICATED_HERE",
        }
    proposals = []
    if rejects["NO_MEANINGFUL_CONTRIBUTION"] >= 2:
        proposals.append({
            "hypothesis": "PRIORITIZE_DOCUMENTED_BUSINESS_OUTCOME_AND_BOUNDED_ROLE",
            "why": "Multiple owner rejections cited no meaningful contribution.",
            "requires_owner_approval": True,
        })
    if rejects["TIMING_NOT_COMPELLING"] >= 2:
        proposals.append({
            "hypothesis": "REQUIRE_FRESHER_VERIFIED_BUSINESS_TRIGGERS",
            "why": "Multiple owner rejections cited an unconvincing engagement time.",
            "requires_owner_approval": True,
        })
    if rejects["EXISTING_OWNER_OVERLAP"] >= 2:
        proposals.append({
            "hypothesis": "EXPAND_COMPLEMENTARY_OWNERSHIP_RESEARCH",
            "why": "Multiple owner rejections cited overlap with current leadership.",
            "requires_owner_approval": True,
        })
    return {
        "status": "HUMAN_REVIEW_ONLY" if proposals else "NO_ACTIONABLE_PATTERN",
        "reviewed": len(unique), "by_decision": dict(verdicts),
        "rejection_reasons": dict(rejects), "proposals": proposals,
        "auto_applied": False, "policy_modified": False,
        "source_assurance": "OPERATOR_SUPPLIED_FEEDBACK_NOT_AUTHENTICATED_HERE",
    }
