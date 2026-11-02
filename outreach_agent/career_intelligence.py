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
RESEARCH_STATES = {"DISCOVERED", "ASSESSABLE", "EVIDENCE_HOLD",
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
    # Requisition IDs are identifiers, even when JSON/PowerShell serializers
    # accidentally encode all-digit IDs as numbers. Compare their textual form
    # while preserving leading zeroes on the canonical job ID.
    if object_id and str(item.get("object_id")) != str(object_id):
        return None
    if kind == "CURRENT_EXECUTIVE_ROLE" and _day(item["retrieved_at"]) < date.today() - timedelta(days=90):
        return None
    if kind == "EXECUTIVE_OWNERSHIP":
        published = _day(item.get("published_on"))
        # A recent page retrieval cannot make a historical executive mention
        # evidence of present initiative ownership.
        if (not published or published < date.today() - timedelta(days=90)
                or _day(item.get("retrieved_at")) < date.today() - timedelta(days=90)):
            return None
    return item


def _decision(state, readiness, reasons, *, pathway, application=False,
              hiring_evidence=None):
    reason_set = set(reasons)
    if "ROLE_OUTSIDE_TARGET_FUNCTION" in reason_set:
        fit_status = "OUT_OF_SCOPE"
    elif "MANDATORY_QUALIFICATION_GAP" in reason_set:
        fit_status = "GAP_CONFIRMED"
    elif reason_set.intersection({"MANDATORY_QUALIFICATION_UNVERIFIED",
                                  "WORK_LOCATION_UNVERIFIED",
                                  "WORK_AUTHORIZATION_UNVERIFIED",
                                  "CITIZENSHIP_UNVERIFIED",
                                  "REMOTE_ELIGIBILITY_UNVERIFIED",
                                  "ROLE_RELEVANCE_UNVERIFIED"}):
        fit_status = "UNVERIFIED"
    else:
        fit_status = "NOT_ASSESSED"
    return {
        "schema_version": VERSION,
        "research_state": state,
        "engagement_readiness": readiness,
        "reasons": sorted(set(reasons)),
        "pathway": pathway,
        "hiring_evidence": (hiring_evidence if hiring_evidence is not None else
                            "STRATEGIC_ACTIVITY_NO_HIRING_EVIDENCE" if pathway == "STRATEGIC_EXPLORATION" else
                            "UNVERIFIED_OR_INACTIVE"),
        "manual_application": "OWNER_AUTH_REQUIRED" if application else "NOT_ELIGIBLE",
        "source_assurance": "SELF_REPORTED_STRUCTURAL_METADATA_NOT_INDEPENDENTLY_WEB_VERIFIED",
        "candidate_fit_status": fit_status,
        "owner_decision": "NOT_REVIEWED",
        "private_history_checked": False,
        "contact_ready": False,
        "draft_approved": False,
        "send_authorized": False,
        "outbound_sent": False,
        "application_submitted": False,
    }


def _qualification_assessment(job):
    items = job.get("mandatory_qualifications")
    if not isinstance(items, list) or not items:
        if job.get("mandatory_requirements_met") is True:
            return [{"requirement": "Legacy aggregate assertion", "status": "UNVERIFIED"}]
        return [{"requirement": "Mandatory qualifications", "status": "UNVERIFIED"}]
    result = []
    for item in items:
        if not isinstance(item, dict):
            result.append({"requirement": "Qualification record", "status": "UNVERIFIED"})
            continue
        status = item.get("status")
        refs = item.get("candidate_evidence_refs")
        if status in ("MATCHED", "GAP") and not (
                isinstance(refs, list) and refs
                and all(isinstance(ref, str) and ref.strip() for ref in refs)):
            status = "UNVERIFIED"
        result.append({"requirement": item.get("requirement", "Unspecified qualification"),
                       "status": status if status in ("MATCHED", "GAP", "UNVERIFIED")
                       else "UNVERIFIED"})
    return result


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
    job = record.get("job") or {}
    hiring_evidence = ("STRATEGIC_ACTIVITY_NO_HIRING_EVIDENCE"
                       if pathway == "STRATEGIC_EXPLORATION"
                       else "UNVERIFIED_OR_INACTIVE")

    def decision(state, readiness, reasons, *, application=False):
        result = _decision(state, readiness, reasons, pathway=pathway,
                           application=application,
                           hiring_evidence=hiring_evidence)
        qualification_assessment = (_qualification_assessment(job)
                                    if pathway == "DIRECT_HIRING" else [])
        result["qualification_assessment"] = qualification_assessment
        eligibility = job.get("candidate_eligibility") or {}
        result["eligibility_assessment"] = {
            "work_mode_feasible": job.get("work_mode_feasible"),
            "work_authorization": eligibility.get("work_authorization", "UNVERIFIED"),
            "citizenship_required": job.get("citizenship_required", "UNKNOWN"),
            "citizenship": eligibility.get("citizenship", "UNVERIFIED"),
            "remote_eligibility": job.get("remote_eligibility", "NOT_APPLICABLE"),
        }
        result["role_relevance"] = (job.get("role_relevance", "UNVERIFIED")
                                     if pathway == "DIRECT_HIRING" else "NOT_APPLICABLE")
        if pathway == "STRATEGIC_EXPLORATION":
            if (isinstance(thesis.get("candidate_basis"), str)
                    and thesis["candidate_basis"].strip()
                    and isinstance(thesis.get("proposed_value"), str)
                    and thesis["proposed_value"].strip()):
                result["candidate_fit_status"] = "CONTRIBUTION_HYPOTHESIS_REPORTED"
        elif (not set(reasons).intersection({
                  "MANDATORY_QUALIFICATION_GAP", "MANDATORY_QUALIFICATION_UNVERIFIED",
                  "WORK_LOCATION_INELIGIBLE", "WORK_LOCATION_UNVERIFIED",
                  "WORK_AUTHORIZATION_INELIGIBLE", "WORK_AUTHORIZATION_UNVERIFIED",
                  "CITIZENSHIP_REQUIREMENT_NOT_MET", "CITIZENSHIP_UNVERIFIED",
                  "ARIZONA_REMOTE_INELIGIBLE", "REMOTE_ELIGIBILITY_UNVERIFIED",
                  "ROLE_OUTSIDE_TARGET_FUNCTION", "ROLE_RELEVANCE_UNVERIFIED"})
              and thesis.get("candidate_claim_approved") is True
              and qualification_assessment
              and all(item["status"] == "MATCHED" for item in qualification_assessment)
              and job.get("role_relevance") in ("MATCH", "ADJACENT")
              and job.get("work_mode_feasible") is True
              and eligibility.get("work_authorization") == "ELIGIBLE"
              and (org.get("work_mode") != "US_REMOTE"
                   or job.get("remote_eligibility") == "AZ_ELIGIBLE")):
            result["candidate_fit_status"] = (
                "REPORTED_ADJACENT_FIT" if job.get("role_relevance") == "ADJACENT"
                else "REPORTED_MATCH")
        return result
    reasons = []
    project_record = {"project_id": record.get("project_id"),
                      "outreach_purpose": record.get("purpose", ""),
                      "why_connect": thesis.get("proposed_value", "")}
    reasons.extend(scope_reasons(project_record, require_project_id=True))
    if reasons:
        return decision("EXCLUDED", "NOT_PREPARED", reasons)
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
    # Diagnose independent issues before choosing the final fail-closed state.
    # Earlier versions returned on the first job defect and hid stale executive
    # roles, unsupported ownership edges, or missing person-specific routes.
    preliminary_reasons = bool(reasons)
    job_reasons = []
    job_closed = False
    application = False
    role_out_of_scope = False
    if pathway == "DIRECT_HIRING":
        job_id = job.get("requisition_id")
        job_claim = _claim(claims, job.get("status_claim_id"),
                           kind="JOB_ACTIVE", subject=org.get("organization_id"),
                           object_id=job_id)
        if job.get("state") == "CLOSED":
            job_closed = True
            hiring_evidence = "EXPIRED_OR_WITHDRAWN"
            reasons.append("JOB_CLOSED")
        else:
            if (not job_id or not _url(job.get("official_ats_url")) or
                    not job_claim or job.get("state") != "ACCEPTING"):
                job_reasons.append("JOB_STATUS_UNVERIFIED")
            elif _day(job_claim.get("retrieved_at")) < date.today() - timedelta(days=7):
                job_reasons.append("JOB_STATUS_STALE")
            if job_claim and job_claim.get("source_url") != job.get("official_ats_url"):
                job_reasons.append("JOB_PRIMARY_SOURCE_MISMATCH")
            status_fresh = bool(job_claim and
                                _day(job_claim.get("retrieved_at")) >= date.today() - timedelta(days=7))
            if (job_id and _url(job.get("official_ats_url")) and job_claim
                    and job.get("state") == "ACCEPTING" and status_fresh
                    and job_claim.get("source_url") == job.get("official_ats_url")):
                hiring_evidence = "ACTIVE_POSTED_ROLE"
            # New packets classify each mandatory qualification as MATCHED,
            # GAP, or UNVERIFIED. The old false boolean conflated a proven gap
            # with missing candidate evidence, so fail closed without claiming
            # a deficiency that was not established.
            qualifications = job.get("mandatory_qualifications")
            if isinstance(qualifications, list) and qualifications:
                normalized = []
                for item in qualifications:
                    if not isinstance(item, dict):
                        normalized.append("UNVERIFIED")
                        continue
                    status = item.get("status")
                    refs = item.get("candidate_evidence_refs")
                    if status in ("MATCHED", "GAP") and not (
                            isinstance(refs, list) and refs
                            and all(isinstance(ref, str) and ref.strip() for ref in refs)):
                        status = "UNVERIFIED"
                    normalized.append(status)
                statuses = set(normalized)
                if "GAP" in statuses:
                    job_reasons.append("MANDATORY_QUALIFICATION_GAP")
                if ("UNVERIFIED" in statuses
                        or statuses - {"MATCHED", "GAP", "UNVERIFIED"}):
                    job_reasons.append("MANDATORY_QUALIFICATION_UNVERIFIED")
            else:
                # The legacy aggregate boolean cannot show which qualification
                # was checked or what candidate evidence supported the match.
                job_reasons.append("MANDATORY_QUALIFICATION_UNVERIFIED")
            if job.get("work_mode_feasible") is False:
                job_reasons.append("WORK_LOCATION_INELIGIBLE")
            elif job.get("work_mode_feasible") is not True:
                job_reasons.append("WORK_LOCATION_UNVERIFIED")
            eligibility = job.get("candidate_eligibility") or {}
            if eligibility.get("work_authorization") == "INELIGIBLE":
                job_reasons.append("WORK_AUTHORIZATION_INELIGIBLE")
            elif eligibility.get("work_authorization") != "ELIGIBLE":
                job_reasons.append("WORK_AUTHORIZATION_UNVERIFIED")
            if (job.get("citizenship_required") is True
                    and eligibility.get("citizenship") not in ("ELIGIBLE", "INELIGIBLE")):
                job_reasons.append("CITIZENSHIP_UNVERIFIED")
            elif (job.get("citizenship_required") is True
                  and eligibility.get("citizenship") == "INELIGIBLE"):
                job_reasons.append("CITIZENSHIP_REQUIREMENT_NOT_MET")
            elif (job.get("citizenship_required") is True
                  and eligibility.get("citizenship") not in ("ELIGIBLE", "INELIGIBLE")):
                job_reasons.append("CITIZENSHIP_UNVERIFIED")
            if org.get("work_mode") == "US_REMOTE":
                remote = job.get("remote_eligibility")
                if remote == "NOT_AZ_ELIGIBLE":
                    job_reasons.append("ARIZONA_REMOTE_INELIGIBLE")
                elif remote != "AZ_ELIGIBLE":
                    job_reasons.append("REMOTE_ELIGIBILITY_UNVERIFIED")
            if job.get("role_relevance") == "OUT_OF_SCOPE":
                role_out_of_scope = True
                reasons.append("ROLE_OUTSIDE_TARGET_FUNCTION")
            elif job.get("role_relevance") not in ("MATCH", "ADJACENT"):
                job_reasons.append("ROLE_RELEVANCE_UNVERIFIED")
            reasons.extend(job_reasons)
            application = not job_reasons and not preliminary_reasons and not role_out_of_scope

    # Neither pathway permits a fabricated need for leadership.
    if thesis.get("leadership_need_assumed") is True:
        reasons.append("INVENTED_LEADERSHIP_GAP")

    executive_reasons = []
    suppressed = False
    if executive is None:
        executive_reasons.append(
            "EXECUTIVE_OWNER_UNVERIFIED" if pathway == "STRATEGIC_EXPLORATION"
            else "HIRING_SPONSOR_NOT_IDENTIFIED"
        )
    elif not isinstance(executive, dict):
        raise ValueError("executive must be object or null")
    elif executive.get("opted_out") is True:
        # Suppression belongs to this person, not a separate employer vacancy.
        suppressed = True
        executive_reasons.append("OPT_OUT_SUPPRESSION")
    else:
        owner_edge = executive.get("ownership") or {}
        role = owner_edge.get("role_type")
        if role not in ROLE_TYPES or owner_edge.get("ownership_grade") != "DOCUMENTED":
            executive_reasons.append("EXECUTIVE_OWNER_UNVERIFIED")
        elif not _claim(claims, owner_edge.get("claim_id"),
                        kind="EXECUTIVE_OWNERSHIP", subject=executive.get("person_id"),
                        object_id=(initiative.get("initiative_id")
                                   if pathway == "STRATEGIC_EXPLORATION"
                                   else job.get("requisition_id"))):
            executive_reasons.append("EXECUTIVE_OWNERSHIP_SOURCE_MISSING")
        if not _claim(claims, executive.get("current_role_claim_id"),
                      kind="CURRENT_EXECUTIVE_ROLE", subject=executive.get("person_id")):
            executive_reasons.append("CURRENT_EXECUTIVE_ROLE_UNVERIFIED")
        route = executive.get("route") or {}
        if (route.get("route_type") not in ("DIRECT", "MANUAL", "WARM_INTRO")
                or route.get("verified_for_person") is not True
                or not _url(route.get("url"))):
            executive_reasons.append("NO_VERIFIED_PERSON_ROUTE")
    reasons.extend(executive_reasons)

    # State precedence is independent of diagnostic completeness. Employer
    # vacancies can survive missing managers; no route is inferred or sent.
    if job_closed:
        return decision("CLOSED_INACTIVE", "NOT_PREPARED", reasons)
    if role_out_of_scope:
        return decision("EXCLUDED", "NOT_PREPARED", reasons)
    if job_reasons or "INVENTED_LEADERSHIP_GAP" in reasons:
        return decision("EVIDENCE_HOLD", "NOT_PREPARED", reasons)
    if preliminary_reasons:
        # V2.1 uses EVIDENCE_HOLD for material claim, identity or
        # feasibility defects; incomplete candidate preparation alone
        # remains DISCOVERED, not engagement-only RESEARCH_PENDING.
        evidence_holds = {
            "OBJECTIVE_NOT_SOURCE_SUPPORTED", "DUPLICATE_CLAIM_ID",
            "CONTRIBUTION_NOT_LINKED_TO_OBJECTIVE", "UNSUPPORTED_HIRING_CLAIM",
            "ORGANIZATION_IDENTITY_MISSING", "WORK_ARRANGEMENT_NOT_CONFIRMED",
        }
        state = ("EVIDENCE_HOLD" if evidence_holds.intersection(reasons)
                 else "DISCOVERED")
        return decision(state, "NOT_PREPARED", reasons)
    if suppressed:
        return decision("ASSESSABLE", "SUPPRESSED", reasons,
                        application=application)
    if executive_reasons:
        return decision("ASSESSABLE", "RESEARCH_PENDING", reasons,
                        application=application)
    return decision("ASSESSABLE", "ENGAGEMENT_REVIEW_ELIGIBLE", reasons,
                    application=application)


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
    # initiative_id is already the stable, source-backed scope when a narrower
    # mandate_key has not been supplied. Falling back to it preserves identity
    # without inventing a mandate or collapsing distinct initiatives.
    scope = scope or initiative
    return ((ident, "STRATEGIC", initiative, scope), None) if initiative else (None, "IDENTITY_COLLISION_HOLD")


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
    for record, result, identity in zip(records, results, keys):
        result["organization_id"] = (record.get("organization") or {}).get("organization_id")
        result["opportunity_identity"] = identity
    counts = Counter(x["research_state"] for x in results)
    return {"schema_version": VERSION, "reviewed": len(records),
            "research_states": dict(counts), "identity_holds": collisions,
            "owner_approved": 0, "new_contact_ready": 0,
            "messages_sent": 0, "applications_submitted": 0,
            "send_authorized": False, "results": results}
