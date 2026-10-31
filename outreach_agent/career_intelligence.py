"""V2.1 offline structural opportunity assessor.

This module cannot visit pages, authenticate a reviewer, read protected memory,
certify a live vacancy, send messages, or submit applications. A valid source
metadata record is NOT independent verification that the linked page is true.
"""
from __future__ import annotations

from collections import Counter
from datetime import date, timedelta
from urllib.parse import urlparse
import re

from .project_scope import PROJECT_ID, scope_reasons

VERSION = "2.1"
THEMES = {"AI_STRATEGY_TRANSFORMATION", "ENTERPRISE_PRODUCT_LEADERSHIP", "BOTH"}
PATHWAYS = {"STRATEGIC_EXPLORATION", "DIRECT_HIRING"}
DECISIONS = {"PURSUE", "RESEARCH_MORE", "REJECT"}
ROLE_TYPES = {"STRATEGIC_SPONSOR", "BUSINESS_OUTCOME_OWNER",
              "AI_OR_TECHNICAL_EXECUTION_OWNER", "PRODUCT_PORTFOLIO_OWNER",
              "HIRING_SPONSOR", "INTRODUCER"}
ROUTES = {"DIRECT", "MANUAL", "WARM_INTRO", "INDIRECT_GENERAL", "NO_ROUTE"}
RESEARCH_STATES = {"ASSESSABLE", "RESEARCH_PENDING", "EVIDENCE_HOLD",
                   "CLOSED_INACTIVE", "EXCLUDED"}
ENGAGEMENT_STATES = {"RESEARCH_PENDING", "ENGAGEMENT_REVIEW_ELIGIBLE",
                     "SUPPRESSED", "NOT_PREPARED"}


def _day(value):
    try:
        return date.fromisoformat(value)
    except (TypeError, ValueError):
        return None


def _url(value):
    if not isinstance(value, str):
        return False
    try:
        u = urlparse(value)
    except ValueError:
        return False
    return u.scheme == "https" and bool(u.hostname) and not (u.username or u.password) and not re.search(r"\s", value)


def _claim_ok(claim):
    if not isinstance(claim, dict):
        return False
    required = ("claim_id", "claim_type", "claim_text", "source_url",
                "publisher", "source_origin_id", "retrieved_at", "excerpt")
    if not all(isinstance(claim.get(x), str) and claim[x].strip() for x in required):
        return False
    d = _day(claim["retrieved_at"])
    if not d or d > date.today() or not _url(claim["source_url"]):
        return False
    if claim.get("page_read_success") is not True or claim.get("support_relationship") != "DIRECT":
        return False
    if claim["claim_text"].casefold() not in claim["excerpt"].casefold():
        return False
    published = claim.get("published_on")
    if published not in (None, "UNDATED"):
        p = _day(published)
        if not p or p > d:
            return False
    return True


def _claim(claims, claim_id, *, kind=None, subject=None, object_id=None):
    item = claims.get(claim_id)
    if not item or not _claim_ok(item):
        return None
    if kind and item.get("claim_type") != kind:
        return None
    if subject and item.get("subject_id") != subject:
        return None
    if object_id and item.get("object_id") != object_id:
        return None
    if kind == "CURRENT_EXECUTIVE_ROLE" and _day(item["retrieved_at"]) < date.today() - timedelta(days=90):
        return None
    if kind == "EXECUTIVE_OWNERSHIP":
        published = _day(item.get("published_on"))
        if published and published < date.today() - timedelta(days=730):
            return None
    return item


def _decision(state, readiness, reasons, *, pathway, application=False):
    return {
        "schema_version": VERSION,
        "research_state": state,
        "engagement_readiness": readiness,
        "reasons": sorted(set(reasons)),
        "pathway": pathway,
        "hiring_evidence": ("CURRENT_EMPLOYER_POSTING_REPORTED" if application else
                            "STRATEGIC_ACTIVITY_NO_HIRING_EVIDENCE" if pathway == "STRATEGIC_EXPLORATION" else
                            "UNVERIFIED_OR_INACTIVE"),
        "manual_application": "OWNER_AUTH_REQUIRED" if application else "NOT_ELIGIBLE",
        "source_assurance": "SELF_REPORTED_STRUCTURAL_METADATA_NOT_INDEPENDENTLY_WEB_VERIFIED",
        "owner_decision": "NOT_RECORDED_IN_RESEARCH",
        "private_history_checked": False,
        "contact_ready": False,
        "draft_approved": False,
        "send_authorized": False,
        "outbound_sent": False,
        "application_submitted": False,
    }


def evaluate_opportunity(record):
    """Evidence-linked structural preflight; never CONTACT_READY or permission to act."""
    if not isinstance(record, dict):
        raise ValueError("Opportunity must be an object")
    if record.get("schema_version") != VERSION:
        raise ValueError("Expected schema_version 2.1")
    pathway = record.get("engagement_pathway")
    if pathway not in PATHWAYS or record.get("capability_theme") not in THEMES:
        raise ValueError("Invalid independent capability/pathway axes")
    org, initiative = record.get("organization") or {}, record.get("initiative") or {}
    thesis = record.get("contribution") or {}
    executive = record.get("executive")
    reasons = []
    project_record = {"project_id": record.get("project_id"),
                      "outreach_purpose": record.get("purpose", ""),
                      "why_connect": thesis.get("proposed_value", "")}
    reasons.extend(scope_reasons(project_record, require_project_id=True))
    if reasons:
        return _decision("EXCLUDED", "NOT_PREPARED", reasons, pathway=pathway)
    if not all(isinstance(org.get(k), str) and org[k].strip() for k in ("organization_id", "name")):
        reasons.append("ORGANIZATION_IDENTITY_MISSING")
    if org.get("work_mode") not in ("TUCSON", "US_REMOTE", "OTHER"):
        reasons.append("WORK_MODE_UNKNOWN")
    if org.get("work_mode") == "OTHER" and org.get("feasible") is not True:
        reasons.append("WORK_ARRANGEMENT_NOT_CONFIRMED")
    evidence = record.get("claims", [])
    if not isinstance(evidence, list) or not all(isinstance(x, dict) for x in evidence):
        raise ValueError("claims must be a list of objects")
    ids = [x.get("claim_id") for x in evidence]
    if len(set(ids)) != len(ids):
        reasons.append("DUPLICATE_CLAIM_ID")
    claims = {x.get("claim_id"): x for x in evidence}
    objective = _claim(claims, initiative.get("objective_claim_id"),
                       kind="BUSINESS_OBJECTIVE",
                       subject=org.get("organization_id"))
    if not objective and pathway == "STRATEGIC_EXPLORATION":
        reasons.append("OBJECTIVE_NOT_SOURCE_SUPPORTED")
    if not isinstance(thesis.get("candidate_basis"), str) or len(thesis["candidate_basis"].strip()) < 15:
        reasons.append("CANDIDATE_BASIS_MISSING")
    if not isinstance(thesis.get("proposed_value"), str) or len(thesis["proposed_value"].strip()) < 20:
        reasons.append("SPECIFIC_CONTRIBUTION_MISSING")
    # The resume-based experience claim still requires independent human review.
    if thesis.get("candidate_claim_approved") is not True:
        reasons.append("UNAPPROVED_CANDIDATE_CLAIM")
    if pathway == "STRATEGIC_EXPLORATION" and thesis.get("business_objective_claim_id") != initiative.get("objective_claim_id"):
        reasons.append("CONTRIBUTION_NOT_LINKED_TO_OBJECTIVE")
    if thesis.get("hiring_claim") is True and pathway == "STRATEGIC_EXPLORATION":
        reasons.append("UNSUPPORTED_HIRING_CLAIM")
    if reasons:
        return _decision("RESEARCH_PENDING", "NOT_PREPARED", reasons, pathway=pathway)

    job = record.get("job") or {}
    application = False
    if pathway == "DIRECT_HIRING":
        job_id = job.get("requisition_id")
        job_claim = _claim(claims, job.get("status_claim_id"),
                           kind="JOB_ACTIVE", subject=org.get("organization_id"),
                           object_id=job_id)
        if job.get("state") == "CLOSED":
            return _decision("CLOSED_INACTIVE", "NOT_PREPARED", ["JOB_CLOSED"], pathway=pathway)
        if (not job_id or not _url(job.get("official_ats_url")) or
                not job_claim or job.get("state") != "ACCEPTING"):
            reasons.append("JOB_STATUS_UNVERIFIED")
        elif _day(job_claim.get("retrieved_at")) < date.today() - timedelta(days=7):
            reasons.append("JOB_STATUS_STALE")
        if job_claim and job_claim.get("source_url") != job.get("official_ats_url"):
            reasons.append("JOB_PRIMARY_SOURCE_MISMATCH")
        if job.get("mandatory_requirements_met") is not True:
            reasons.append("MANDATORY_QUALIFICATION_GAP")
        if job.get("work_mode_feasible") is not True:
            reasons.append("WORK_LOCATION_INELIGIBLE")
        if reasons:
            return _decision("EVIDENCE_HOLD", "NOT_PREPARED", reasons, pathway=pathway)
        application = True

    # An accepted strategic research finding may have no named executive.
    if pathway == "STRATEGIC_EXPLORATION" and thesis.get("leadership_need_assumed") is True:
        return _decision("EVIDENCE_HOLD", "NOT_PREPARED", ["INVENTED_LEADERSHIP_GAP"], pathway=pathway)
    if executive is None:
        return _decision("ASSESSABLE", "RESEARCH_PENDING",
                         ["EXECUTIVE_OWNER_UNVERIFIED"] if pathway == "STRATEGIC_EXPLORATION"
                         else ["HIRING_SPONSOR_NOT_IDENTIFIED"],
                         pathway=pathway, application=application)
    if not isinstance(executive, dict):
        raise ValueError("executive must be object or null")
    if executive.get("opted_out") is True:
        return _decision("ASSESSABLE", "SUPPRESSED", ["OPT_OUT_SUPPRESSION"],
                         pathway=pathway, application=application)

    owner_edge = executive.get("ownership") or {}
    role = owner_edge.get("role_type")
    if role not in ROLE_TYPES or owner_edge.get("ownership_grade") != "DOCUMENTED":
        reasons.append("EXECUTIVE_OWNER_UNVERIFIED")
    elif not _claim(claims, owner_edge.get("claim_id"),
                    kind="EXECUTIVE_OWNERSHIP", subject=executive.get("person_id"),
                    object_id=initiative.get("initiative_id") if pathway == "STRATEGIC_EXPLORATION" else job.get("requisition_id")):
        reasons.append("EXECUTIVE_OWNERSHIP_SOURCE_MISSING")
    if not _claim(claims, executive.get("current_role_claim_id"),
                  kind="CURRENT_EXECUTIVE_ROLE", subject=executive.get("person_id")):
        reasons.append("CURRENT_EXECUTIVE_ROLE_UNVERIFIED")
    route = executive.get("route") or {}
    if (route.get("route_type") not in ("DIRECT", "MANUAL", "WARM_INTRO")
            or route.get("verified_for_person") is not True
            or not _url(route.get("url"))):
        reasons.append("NO_VERIFIED_PERSON_ROUTE")
    return _decision("ASSESSABLE",
                     "RESEARCH_PENDING" if reasons else "ENGAGEMENT_REVIEW_ELIGIBLE",
                     reasons, pathway=pathway, application=application)


def assess_owner_feedback(assessment, research_result):
    """Review preference as a separate event. Cannot upgrade a source or readiness."""
    if not isinstance(assessment, dict) or assessment.get("decision") not in DECISIONS:
        raise ValueError("Invalid owner decision")
    if not isinstance(assessment.get("reason", ""), str):
        raise ValueError("Invalid reason")
    out = dict(research_result)
    out["owner_decision"] = assessment["decision"]
    out["owner_reason"] = assessment["reason"]
    out["owner_attestation"] = "OPERATOR_PROVIDED_NOT_AUTHENTICATED_BY_REFERENCE_MODULE"
    return out


def opportunity_identity(record):
    """Stable distinct opportunity identity. Ambiguity is held, not auto-merged."""
    org = record.get("organization") or {}
    ident = org.get("organization_id")
    if not ident:
        return None, "IDENTITY_COLLISION_HOLD"
    if record.get("engagement_pathway") == "DIRECT_HIRING":
        req = (record.get("job") or {}).get("requisition_id")
        return ((ident, "ATS", req), None) if req else (None, "IDENTITY_COLLISION_HOLD")
    initiative = (record.get("initiative") or {}).get("initiative_id")
    scope = (record.get("contribution") or {}).get("mandate_key")
    return ((ident, "STRATEGIC", initiative, scope), None) if initiative and scope else (None, "IDENTITY_COLLISION_HOLD")


def audit_packet(records):
    """Portfolio summary without quota, invented certified contacts or outreach."""
    if not isinstance(records, list):
        raise ValueError("records must be a list")
    results = [evaluate_opportunity(x) for x in records]
    keys = [opportunity_identity(x)[0] for x in records]
    collisions = [i for i, k in enumerate(keys) if k is None or keys.count(k) > 1]
    for i in collisions:
        results[i] = dict(results[i])
        results[i]["research_state"] = "EVIDENCE_HOLD"
        results[i]["engagement_readiness"] = "NOT_PREPARED"
        results[i]["reasons"] = sorted(set(results[i]["reasons"] + ["IDENTITY_COLLISION_HOLD"]))
        results[i]["manual_application"] = "NOT_ELIGIBLE"
    counts = Counter(x["research_state"] for x in results)
    return {"schema_version": VERSION, "reviewed": len(records),
            "research_states": dict(counts), "identity_holds": collisions,
            "owner_approved": 0, "new_contact_ready": 0,
            "messages_sent": 0, "applications_submitted": 0,
            "send_authorized": False, "results": results}
