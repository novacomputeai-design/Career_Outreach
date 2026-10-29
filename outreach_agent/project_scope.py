"""Fail-closed scope classification for the personal Career Outreach workflow.

Structural defense-in-depth, not a proof of natural-language intent. Never trust
agent-generated scope labels alone; human review and independent evidence remain
mandatory. No business capture or sales objects may enter career recommendations.
"""
from __future__ import annotations
import re

PROJECT_ID = "PERSONAL_CAREER_OUTREACH"
BUSINESS_FIELDS = frozenset({
    "prime_contractor", "prime_contract", "contract_award_id", "award_piid",
    "subcontract_opportunity", "subcontract_budget", "subcontracting_stage",
    "capture_stage", "supplier_registration", "prime_teaming_route",
    "rfq_number", "federal_capture_status", "subcontract_pursuit",
})
# Only scan intentional outreach objectives, never quoted source content:
# government contractors may themselves be legitimate CAREER employers.
BUSINESS_INTENT = re.compile(
    r"\b(?:subcontract(?:ing|or|s)?|prime[- ]contract(?:or|ing)?|"
    r"federal capture|teaming (?:agreement|opportunity|partner)|"
    r"supplier onboarding|bid on (?:an? )?(?:award|rfq|contract)|"
    r"sell (?:our|nova)|pitch nova|nova compute (?:sales|services|capabilities)|"
    r"nova (?:subcontract|federal capture)|"
    r"(?:submit|send) (?:our |a |the )?(?:capability statement|bid|proposal|quote)|"
    r"(?:supplier|vendor) (?:registration|portal|onboarding)|"
    r"(?:pitch|offer|provide|sell) (?:our |nova(?: compute)? |my company'?s? )?"
    r"(?:ai |software |automation |technical )?(?:services|solutions|capabilities)|"
    r"(?:pursue|win|bid for|bid on) (?:a |the )?(?:government |federal )?"
    r"(?:contract|award|task order|solicitation)|"
    r"(?:nova compute|our company)\b.{0,75}\b"
    r"(?:deliver|provide|sell|subcontract|teaming|supplier|services)\b|"
    r"(?:deliver|provide|sell)\b.{0,75}\b(?:to nova|for nova compute))\b",
    flags=re.IGNORECASE,
)
FORBIDDEN_PURPOSES = frozenset({
    "NOVA_SUBCONTRACTING", "NOVA_FEDERAL_CAPTURE", "BUSINESS_DEVELOPMENT",
    "COMMERCIAL_SALES", "SUPPLIER_TEAMING",
})
INTENT_FIELDS = ("why_connect", "outreach_objective", "engagement_goal",
                 "outreach_purpose", "purpose", "draft")


def scope_reasons(record: dict, *, require_project_id: bool = False) -> list[str]:
    if not isinstance(record, dict):
        return ["INVALID_CAREER_PROSPECT"]
    reasons = []
    claimed = record.get("project_id")
    if claimed is not None and claimed != PROJECT_ID:
        reasons.append("PROJECT_ID_MISMATCH")
    if require_project_id and claimed != PROJECT_ID:
        reasons.append("PROJECT_ID_NOT_VERIFIED")
    purpose = str(record.get("purpose", "") or "").upper().strip()
    if purpose in FORBIDDEN_PURPOSES:
        reasons.append("COMMERCIAL_PURPOSE_NOT_PERSONAL_CAREER")
    if BUSINESS_FIELDS.intersection(record):
        reasons.append("CROSS_PROJECT_BUSINESS_CAPTURE_FIELDS")
    for field in INTENT_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and BUSINESS_INTENT.search(value):
            reasons.append("CROSS_PROJECT_COMMERCIAL_OUTREACH_INTENT")
            break
    return sorted(set(reasons))
