"""V1.1 organization-first personal career opportunity precheck.

Structural provenance only: no actual source verification, hiring commitment,
private-memory access, contact readiness or sending authority.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from urllib.parse import urlparse

from .project_scope import PROJECT_ID, scope_reasons

SCHEMA_VERSION = "1.1"
TRACKS = {"AI_STRATEGY", "PRODUCT_LEADERSHIP"}
CLASSES = {"O1", "O2A", "O2B", "O3", "O4"}
SIGNALS = {"POSTED_OPENING", "PUBLIC_ROLE_CREATION_STATEMENT",
           "OWNER_REPORTED_ROLE_DISCUSSION", "NONE"}
ROUTES = {"DIRECT", "MANUAL", "INDIRECT", "NO_ROUTE"}
WORK_MODES = {"TUCSON", "US_REMOTE", "OTHER"}
AUTHORITIES = {"DOCUMENTED_HIRING_SPONSOR", "DOCUMENTED_INITIATIVE_OWNER",
               "POTENTIAL_INFLUENCER", "UNVERIFIED"}
ORG_CAPS = {"strategic_need": 30, "experience_fit": 25,
            "leadership_feasibility": 20, "timeliness": 15, "work_mode": 10}
PERSON_CAPS = {"influence": 30, "initiative_ownership": 25,
               "conversation_value": 20, "route": 15, "role_evidence": 10}
TOP_KEYS = {"schema_version", "project_id", "track", "classification",
            "organization", "strategic_signal", "mandate", "fit",
            "decision_maker", "scores"}
SECTION_KEYS = {
    "organization": {"name", "parent", "work_mode"},
    "strategic_signal": {"claim", "source_url", "published_on", "observed_on"},
    "mandate": {"title_or_function", "employment_signal", "evidence_url",
                "employment_hypothesis"},
    "fit": {"resume_basis", "contribution", "work_arrangement_feasible",
            "credentials_match"},
    "decision_maker": {"name", "current_title", "role_source_url",
                       "initiative_ownership_source_url", "authority",
                       "route_type", "route_url", "conversation_thesis"},
    "scores": {"organization", "person"},
}


def _text(obj, key):
    value = obj.get(key)
    if (not isinstance(value, str) or not value.strip() or len(value) > 1200
            or any(ord(ch) < 32 and ch not in "\n" for ch in value)):
        raise ValueError("Invalid opportunity text: " + key)
    return value.strip()


def _url(value, label, *, required=True):
    if value in ("", None) and not required:
        return ""
    if not isinstance(value, str) or len(value) > 2000:
        raise ValueError("Missing/oversized opportunity URL: " + label)
    parsed = urlparse(value)
    if (parsed.scheme != "https" or not parsed.hostname or parsed.username
            or parsed.password or any(ch.isspace() for ch in value)):
        raise ValueError("Untrusted opportunity URL: " + label)
    return value


def _date(value, label):
    try:
        parsed = date.fromisoformat(value)
    except (ValueError, TypeError) as exc:
        raise ValueError("Invalid date: " + label) from exc
    if parsed > date.today():
        raise ValueError("Future evidence date: " + label)
    return parsed


def _check_schema(record):
    if not isinstance(record, dict) or set(record) != TOP_KEYS:
        raise ValueError("Unexpected V1.1 opportunity fields")
    for key, allowed in SECTION_KEYS.items():
        value = record[key]
        if not isinstance(value, dict) or not set(value).issubset(allowed):
            raise ValueError("Unexpected opportunity section fields: " + key)
    for key, caps in (("organization", ORG_CAPS), ("person", PERSON_CAPS)):
        scores = record["scores"].get(key)
        if not isinstance(scores, dict) or set(scores) != set(caps):
            raise ValueError("Missing or unexpected score factors: " + key)
        for factor, maximum in caps.items():
            amount = scores[factor]
            if (isinstance(amount, bool) or not isinstance(amount, int)
                    or not 0 <= amount <= maximum):
                raise ValueError("Score outside cap: " + factor)


def evaluate_opportunity(record, *, policy=None):
    """Return a conservative precheck. Never return employment/hiring certainty."""
    from .governance import active_policy
    policy = policy or active_policy()
    settings = policy["opportunity_search"]
    _check_schema(record)
    if record["schema_version"] != SCHEMA_VERSION:
        raise ValueError("Opportunity schema version mismatch")
    if record["track"] not in TRACKS or record["classification"] not in CLASSES:
        raise ValueError("Unsupported opportunity track/class")
    reasons = list(scope_reasons(record, require_project_id=True))
    # Business-sales intent can be hidden in nested public rationale fields.
    for rationale in (record["fit"].get("contribution"),
                      record["mandate"].get("title_or_function"),
                      record["decision_maker"].get("conversation_thesis")):
        reasons.extend(scope_reasons(
            {"project_id": PROJECT_ID, "why_connect": rationale},
            require_project_id=True))
    o, s, m, f, p = (record[key] for key in (
        "organization", "strategic_signal", "mandate", "fit", "decision_maker"))
    _text(o, "name")
    _text(o, "parent")
    if o.get("work_mode") not in WORK_MODES:
        raise ValueError("Invalid work mode")
    _text(s, "claim")
    _url(s.get("source_url"), "strategic_signal.source_url")
    observed = _date(s.get("observed_on"), "observed_on")
    published = _date(s["published_on"], "published_on") if s.get("published_on") else None
    if published and published > observed:
        reasons.append("PUBLICATION_AFTER_OBSERVATION")
    if not published or date.today() - published > timedelta(days=730):
        reasons.append("STRATEGIC_SOURCE_FRESHNESS_UNVERIFIED")
    _text(m, "title_or_function")
    if m.get("employment_signal") not in SIGNALS:
        raise ValueError("Invalid employment signal")
    if type(m.get("employment_hypothesis")) is not bool:
        raise ValueError("Employment hypothesis must be boolean")
    mandate_url = _url(m.get("evidence_url"), "mandate.evidence_url", required=False)
    _text(f, "resume_basis")
    _text(f, "contribution")
    if type(f.get("work_arrangement_feasible")) is not bool:
        raise ValueError("Missing work arrangement assessment")
    if type(f.get("credentials_match")) is not bool:
        raise ValueError("Missing credential fit assessment")
    if not f["work_arrangement_feasible"] or o["work_mode"] == "OTHER":
        reasons.append("WORK_ARRANGEMENT_NOT_VERIFIED_FEASIBLE")
    if not f["credentials_match"]:
        reasons.append("REQUIRED_CREDENTIALS_NOT_MATCHED")
    # Employer opportunities must survive research even if the job listing
    # does not disclose an executive. This is NOT permission to contact anyone.
    has_executive = bool(p.get("name"))
    ownership_url = ""
    if has_executive:
        if len(_text(p, "name").split()) < 2:
            reasons.append("PERSON_IDENTITY_INCOMPLETE")
        _text(p, "current_title")
        _text(p, "conversation_thesis")
        _url(p.get("role_source_url"), "decision_maker.role_source_url")
        ownership_url = _url(p.get("initiative_ownership_source_url"),
                             "decision_maker.initiative_ownership_source_url",
                             required=False)
        if p.get("authority") not in AUTHORITIES or p.get("route_type") not in ROUTES:
            raise ValueError("Invalid person authority/route classification")
        route_url = _url(p.get("route_url"), "decision_maker.route_url", required=False)
        if p["route_type"] == "NO_ROUTE" or not route_url:
            reasons.append("NO_PERSON_SPECIFIC_ROUTE")
        if p["route_type"] == "INDIRECT":
            reasons.append("INDIRECT_ROUTE_REQUIRES_PERSON_SPECIFIC_REVIEW")
        if p["authority"] in {"UNVERIFIED", "POTENTIAL_INFLUENCER"}:
            reasons.append("EXECUTIVE_SPONSOR_NOT_ESTABLISHED")
        if p["authority"] == "DOCUMENTED_INITIATIVE_OWNER" and not ownership_url:
            reasons.append("INITIATIVE_OWNERSHIP_SOURCE_MISSING")
    else:
        if any(value not in ("", None, "NO_ROUTE", "UNVERIFIED")
               for value in p.values()):
            reasons.append("PARTIAL_EXECUTIVE_EVIDENCE_NOT_VERIFIED")
    kind, signal = record["classification"], m["employment_signal"]
    if kind == "O1":
        if signal != "POSTED_OPENING" or not mandate_url:
            reasons.append("POSTED_ROLE_EVIDENCE_MISSING")
    elif kind == "O2A":
        if signal == "PUBLIC_ROLE_CREATION_STATEMENT":
            if not mandate_url:
                reasons.append("ROLE_CREATION_SOURCE_MISSING")
        elif signal == "OWNER_REPORTED_ROLE_DISCUSSION":
            reasons.append("OWNER_ATTESTATION_REQUIRED_PRIVATE_REVIEW")
        else:
            reasons.append("EMERGING_MANDATE_UNSUPPORTED")
    elif kind == "O2B":
        if signal != "NONE" or not m["employment_hypothesis"]:
            reasons.append("EXPLORATION_MUST_NOT_CLAIM_HIRING")
        if (p.get("authority") not in {"DOCUMENTED_INITIATIVE_OWNER",
                                      "DOCUMENTED_HIRING_SPONSOR"}
                or not ownership_url):
            reasons.append("ACCOUNTABLE_EXECUTIVE_NOT_CORROBORATED")
    elif kind == "O3":
        reasons.append("GENERAL_RELEVANCE_NOT_ACTIVE_OPPORTUNITY")
    else:
        reasons.append("UNSUITABLE_OR_UNRELIABLE_OPPORTUNITY")
    if kind in {"O1", "O2A"} and m["employment_hypothesis"]:
        reasons.append("MANDATE_CLASSIFICATION_CONFLICT")
    org_score = sum(record["scores"]["organization"].values())
    person_score = sum(record["scores"]["person"].values())
    if org_score < settings["minimum_organization_score"]:
        reasons.append("ORGANIZATION_SCORE_BELOW_THRESHOLD")
    if has_executive and person_score < settings["minimum_decision_maker_score"]:
        reasons.append("DECISION_MAKER_SCORE_BELOW_THRESHOLD")
    if not has_executive and person_score != 0:
        reasons.append("EXECUTIVE_SCORE_WITHOUT_PERSON_EVIDENCE")
    if not has_executive and kind == "O2B":
        reasons.append("ACCOUNTABLE_EXECUTIVE_NOT_CORROBORATED")
    if record["project_id"] != PROJECT_ID:
        reasons.append("PROJECT_ID_NOT_VERIFIED")
    decision = ("RESEARCH_HOLD" if reasons else
                "ORGANIZATION_REVIEW_EXECUTIVE_PENDING" if not has_executive
                else "EXPLORATORY_REVIEW" if kind == "O2B"
                else "SHORTLIST_PENDING_HUMAN_REVIEW")
    return {
        "schema_version": SCHEMA_VERSION, "project_id": PROJECT_ID,
        "classification": kind, "track": record["track"],
        "organization_name": o["name"], "parent_organization": o["parent"],
        "organization_score": org_score, "decision_maker_score": person_score,
        "decision": decision, "reasons": sorted(set(reasons)),
        "hiring_status": ("UNCONFIRMED" if kind == "O2B"
                          else "SOURCE_CLAIM_PENDING_INDEPENDENT_VERIFICATION"),
        "assurance": "STRUCTURAL_SOURCE_CLAIMS_ONLY_NOT_WEB_VERIFIED",
        "private_history_checked": False, "confirmed_new": False,
        "contact_ready": False, "send_authorized": False,
    }


def audit_opportunity_portfolio(assessments, *, pilot_size=5, policy=None):
    """Audit portfolio mix and concentration, never make a contact-ready claim."""
    from .governance import active_policy
    settings = (policy or active_policy())["opportunity_search"]
    if not isinstance(assessments, list) or not all(isinstance(x, dict) for x in assessments):
        raise ValueError("Portfolio must contain opportunity assessments")
    selected = [x for x in assessments if x.get("decision") in {
        "SHORTLIST_PENDING_HUMAN_REVIEW", "EXPLORATORY_REVIEW",
        "ORGANIZATION_REVIEW_EXECUTIVE_PENDING"}]
    tracks = Counter(x["track"] for x in selected)
    parents = Counter(x["parent_organization"].strip().casefold() for x in selected)
    employers = Counter(x["organization_name"].strip().casefold() for x in selected)
    warnings = []
    if any(n > 1 for n in employers.values()):
        warnings.append("DUPLICATE_ORGANIZATION")
    if pilot_size == 5 and any(n > 1 for n in parents.values()):
        warnings.append("PILOT_PARENT_ORGANIZATION_CONCENTRATION")
    if pilot_size == 5 and len(selected) == 5 and (
            tracks["AI_STRATEGY"] != 3 or tracks["PRODUCT_LEADERSHIP"] != 2):
        warnings.append("PILOT_ALLOCATION_DEVIATION")
    return {
        "target": pilot_size, "shortlisted_for_review": len(selected),
        "track_counts": dict(tracks),
        "shortfall": max(0, pilot_size - len(selected)),
        "executive_research_pending": sum(
            x["decision"] == "ORGANIZATION_REVIEW_EXECUTIVE_PENDING"
            for x in selected),
        "portfolio_warnings": warnings,
        "target_allocation": settings["track_allocation"],
        "not_human_approved": True, "new_contact_ready": 0,
        "messages_sent": 0,
    }
