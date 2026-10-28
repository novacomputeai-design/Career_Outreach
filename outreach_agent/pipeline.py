"""Daily research orchestration, conservative evidence verification and report generation.

This runtime can discover leads with permitted search tools. It MUST NOT declare
20 contact-ready people unless both source corroboration and an official professional
contact route are independently observed. No sending code is present.
"""
from __future__ import annotations
import hashlib
import json
import re
import uuid
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from urllib.parse import urlparse
from .research import Tavily, Extractor, discover, Source, host, normalize, qualified_source_pair, url_valid
from .state import PrivateStore
from .learning import summarize
from .contracts import validate_prospect
from .project_scope import PROJECT_ID, scope_reasons

def extract_role_excerpt(source, person_name, current_title):
    """Find a short exact, contiguous passage containing name and title."""
    raw=source.text
    name=re.search(re.escape(person_name), raw, flags=re.I)
    if not name:
        return None
    start=max(0,name.start()-120)
    end=min(len(raw),name.end()+280)
    passage=raw[start:end].strip()
    return passage if normalize(current_title) in normalize(passage) else None

def plausible_official_domain(organization, source_url):
    """Conservative lexical employer-domain check; mismatches require human adjudication."""
    generic={"health","healthcare","systems","company","group","inc","llc","the","and",
             "university","college","city","of","technology","technologies","services"}
    tokens=[x for x in re.findall(r"[a-z0-9]+",organization.casefold())
            if len(x)>=3 and x not in generic]
    hostname=host(source_url)
    return bool(tokens) and any(t in hostname for t in tokens)

def research_enrichment(search, lead):
    """Search independently for role corroboration and a published organization contact route.

    Second evidence needs a DIFFERENT host. Contact route is INDIRECT and must be
    a publicly indexed *contact page*, never a synthesized personal address.
    """
    name=lead["person_name"]
    org=lead["organization"]
    try:
        hits=search.search('"' + name + '" "' + org + '" ' + lead["current_title"], limit=8)
        second=None
        passage=None
        for hit in hits:
            if host(hit.url)==host(lead["source_url"]):
                continue
            q=extract_role_excerpt(hit,name,lead["current_title"])
            if q and qualified_source_pair(lead,hit,q):
                second,passage=hit,q
                break
        if second is None:
            return None, "no_independent_role_corroboration"
        routes=search.search('"' + org + '" official website contact',limit=8)
        route=None
        for hit in routes:
            # Must be an org-owned host from one of the two independently observed sites.
            if host(hit.url) not in (host(lead["source_url"]), host(second.url)):
                continue
            if not plausible_official_domain(org,hit.url):
                continue
            if normalize(org) not in normalize(hit.title+" "+hit.text[:1000]):
                continue
            if not re.search(r"(contact|connect|inquir)",hit.url+" "+hit.title,re.I):
                continue
            if "contact" not in normalize(hit.text) and "email" not in normalize(hit.text):
                continue
            route=hit
            break
        if route is None:
            return None, "no_evidenced_official_contact_route"
        lead=dict(lead)
        lead["second_role_source_url"]=second.url
        lead["second_role_quote"]=passage
        lead["route_url"]=route.url
        lead["route_type"]="INDIRECT"
        lead["route_note"]="General official organization route, not a verified direct path to this executive"
        lead["verified_evidence_grade"]="TWO_DISTINCT_SOURCE_HOSTS"
        return lead,None
    except Exception as exc:
        return None,"source_error_"+type(exc).__name__

def deterministic_score(lead):
    """Transparent provisional 0–100 career-fit heuristic, not hiring probability.

    Mirrors the rubric's 30/25/20/15/10 caps. The model cannot turn an
    executive title into proven hiring authority. Scores require independent
    evidence review and may never override missing-source/novelty HOLD.
    """
    context=normalize(lead["initiative_quote"]+" "+lead["why_connect"])
    terms={
        "product":["product","platform","portfolio","customer"],
        "ai":["ai","artificial intelligence","automation","machine learning"],
        "transformation":["modernization","transformation","enterprise","digital","workflow"],
        "leadership":["strategy","innovation","operational","governance"]
    }
    categories=sum(any(term in context for term in values) for values in terms.values())
    alignment=min(30,10+categories*4+(4 if len(lead["initiative_quote"])>=90 else 0))
    job=normalize(lead["current_title"])
    # Seniority is only a proxy for POTENTIAL influence, never verified hiring.
    if any(k in job for k in ("chief","ceo","president")):
        influence=22
    elif "vice president" in job or job.startswith("vp ") or job.startswith("vp,"):
        influence=20
    elif "director" in job or "head of" in job:
        influence=17
    else:
        influence=9
    conversation=min(20,10+
        (4 if len(lead["initiative_quote"])>=60 else 0)+
        (4 if len(lead["why_connect"])>=55 else 0)+
        (2 if len(lead["initiative_quote"])>=120 else 0))
    # General corporate form is an INDIRECT route, never a person-specific one.
    reachability={"INDIRECT":7,"MANUAL":9,"DIRECT":13}.get(lead.get("route_type"),0)
    geography=10 if lead["segment"]=="tucson" else (8 if lead["segment"]=="remote" else 4)
    scores={"alignment":alignment,"influence":influence,"conversation":conversation,
            "reachability":reachability,"geography":geography}
    return scores,sum(scores.values())

def proposal(lead):
    """Evidence-specific UNSENT draft; never a generic bulk introduction."""
    from .project_scope import scope_reasons
    if scope_reasons(lead, require_project_id=True):
        raise ValueError("Personal career scope HOLD: cannot prepare sales outreach")
    name=lead["person_name"].split()[0]
    organization=lead["organization"].strip()
    quote=" ".join(lead["initiative_quote"].split())
    reason=" ".join(lead["why_connect"].split()).rstrip(".")
    if len(quote)<25 or len(reason)<25:
        raise ValueError("Evidence-specific draft requires a substantive reason")
    # Do not blindly paste an unbounded externally supplied text block into
    # an outbound message. Exact content still requires independent review.
    quote=quote[:180].rstrip(" ,;:")
    reason=reason[:160].rstrip(" ,;:")
    return (
        f"Hello {name},\\n\\n"
        f"I came across {organization}'s work and a specific initiative caught my eye: "
        f"\\\"{quote}\\\"\\n\\n"
        f"My background includes leading enterprise product strategy, technology "
        f"modernization and practical AI adoption. One topic I'd enjoy discussing "
        f"is {reason[0].lower()+reason[1:]}.\\n\\n"
        f"Would you be open to a brief conversation to exchange perspectives?\\n\\n"
        f"Best regards,\\nFadi"
    )

def make_brief(search, extractor, store, target=20, max_queries=14, max_enrich=48, queries=None):
    """Run one daily cycle. Stored recommendations prevent repeated 'new' counts."""
    rid="run-"+uuid.uuid4().hex
    store.start_run(rid)
    date=datetime.now(ZoneInfo("America/Phoenix")).date().isoformat()
    report={"run_id":rid,"date_local":date,"timezone":"America/Phoenix","target":target,"discoveries":0,
            "new_contact_ready":0,"drafts_sent":0,"confirmed_sent":0,
            "source_corroborated_pending_human_review":0,
            "candidates":[],"held":[],"source_errors":[],"stage":"IN_PROGRESS",
            "audit_status":"NOT_RUN","novelty_source":"encrypted_private_store"}
    try:
        leads,errors=discover(search,extractor,queries=queries,max_queries=max_queries,max_records=max_enrich*2)
        report["discoveries"]=len(leads)
        report["source_errors"]=errors
        prior_in_batch=set()
        for lead in leads:
            name_key=normalize(lead["person_name"])
            if name_key in prior_in_batch:
                report["held"].append({"name":lead["person_name"],"reason":"duplicate_current_batch"})
                continue
            prior_in_batch.add(name_key)
            # EARLY private dedup before expensive enrichment
            if store.match(lead):
                report["held"].append({"name":lead["person_name"],"reason":"existing_or_ambiguous_identity"})
                continue
            enriched,reason=research_enrichment(search,lead)
            if not enriched:
                report["held"].append({"name":lead["person_name"],"reason":reason})
                if reason=="source_error_BudgetExceeded":
                    report["source_errors"].append({"stage":"enrichment","error_type":"BudgetExceeded"})
                    break
                continue
            scores,total=deterministic_score(enriched)
            if total<70:
                report["held"].append({"name":lead["person_name"],"reason":"score_below_70","score":total})
                continue
            enriched["project_id"]=PROJECT_ID
            enriched["scores"]=scores
            enriched["score_total"]=total
            enriched["draft"]=proposal(enriched)
            enriched["draft_status"]="PENDING_CONTENT_APPROVAL"
            # Pre-report evidence audit (not fully independent adversarial qualification).
            if not audit_record(enriched):
                report["held"].append({"name":lead["person_name"],"reason":"failed_deterministic_evidence_audit"})
                continue
            try:
                person_id=store.register(enriched,enriched["segment"],run_id=rid)
            except ValueError:
                report["held"].append({"name":lead["person_name"],"reason":"identity_conflict_on_commit"})
                continue
            enriched["person_id"]=person_id
            # The record and draft are sensitive; output report MUST stay outside public Git.
            report["candidates"].append(enriched)
            if len(report["candidates"])>=target:
                break
        report["source_corroborated_pending_human_review"]=len(report["candidates"])
        # Human review is a separate observed event, never an inferred provider success.
        report["new_contact_ready"]=0
        report["production_verified_contact_ready"]=0
        report["shortfall"]=max(0,target-report["new_contact_ready"])
        report["research_shortfall"]=max(0,target-report["source_corroborated_pending_human_review"])
        if report["source_errors"] and not leads:
            report["stage"]="PARTIAL_SOURCE_FAILURE"
        elif report["source_errors"]:
            report["stage"]="COMPLETE_WITH_SOURCE_ERRORS"
        else:
            report["stage"]="COMPLETE_WITH_SHORTFALL" if report["shortfall"] else "COMPLETE"
        report["audit_status"]="DETERMINISTIC_EVIDENCE_PRECHECK_ONLY"
        report["qualification_warning"]="SOURCE-CORROBORATED IS NOT CONTACT-READY. Second distinct-host source corroboration is not a guarantee of current affiliation or reachable hiring authority; human review remains required."
        store.finish_run(rid,report["stage"],report)
    except Exception as exc:
        report["stage"]="FAILED"
        report["error_type"]=type(exc).__name__
        store.finish_run(rid,"FAILED",{"error_type":type(exc).__name__})
        raise
    return report

def audit_record(record):
    needed=("person_name","current_title","organization","source_url","second_role_source_url",
            "role_quote","second_role_quote","initiative_quote","why_connect","route_url",
            "route_type","observed_on","scores","score_total")
    if scope_reasons(record, require_project_id=True):
        return False
    if any(not record.get(k) for k in needed):
        return False
    if validate_prospect(record):
        return False
    urls=[record["source_url"],record["second_role_source_url"],record["route_url"]]
    if not all(url_valid(u) for u in urls) or host(urls[0])==host(urls[1]):
        return False
    if record["route_type"]!="INDIRECT" or host(urls[2]) not in (host(urls[0]),host(urls[1])):
        return False
    return record["score_total"]>=70 and sum(record["scores"].values())==record["score_total"]
