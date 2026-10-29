"""Generate an UNAPPROVED public research packet for Fadi's Drive review tracker.

No network, private database, Google auth, model calls, email, or sending.
This is a local Codex-output-to-Google-review handoff, NOT a memory broker.
"""
from __future__ import annotations
import csv
import hashlib
import json
import re
from datetime import date
from pathlib import Path
from urllib.parse import urlparse
from .project_scope import PROJECT_ID, scope_reasons

PROSPECT_HEADERS = [
    "Person ID","Name","Organization","Current Role","Geography","Category",
    "Specific Career Reason","Current Role Source URL","Initiative Source URL",
    "Observed On","Evidence Status","Local Memory Status","Novelty Status",
    "Contact Route","Contact Route URL","Fit Score","Fadi Review","Updated On","Run ID"
]
RUN_HEADERS = [
    "Run ID","Local Date (Phoenix)","Research Scope","People Considered",
    "Evidence Prechecked","Held","Drafts Prepared","Human Reviewed",
    "Actually Sent (manual)","Source Failures","Shortfall","Run Status",
    "Brief URL","Notes (non-sensitive)"
]
ALLOWED = {
    "person_name","organization","current_title","segment","category",
    "why_connect","role_source_url","reason_source_url","observed_on",
    "route_type","route_url","score_total","profile_url","project_id"
}
CATEGORIES = {"hiring-influencer","strategic-connector","hiring-decision-maker",
              "unknown"}
SEGMENTS = {"tucson","remote","other"}
ROUTES = {"DIRECT","INDIRECT","MANUAL","NO_ROUTE"}
MAX_PEOPLE = 20
MAX_BYTES = 65536


def _text(value, field, *, required=True, limit=600):
    if value is None and not required:
        return ""
    if not isinstance(value,str) or len(value.strip()) > limit or (
        required and not value.strip()
    ) or any(ord(c)<32 and c not in "\n" for c in value):
        raise ValueError(f"Invalid public research field: {field}")
    return " ".join(value.split())


def _url(value,field,*,required=False):
    if value in ("",None) and not required:
        return ""
    u = _text(value,field,limit=2000)
    parsed=urlparse(u)
    if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password or any(c.isspace() for c in u):
        raise ValueError(f"Invalid public HTTPS source: {field}")
    return u


def _csv_safe(value):
    s=str(value)
    if s.lstrip().startswith(("=","+","-","@")) or s.startswith(("\t","\r","\n")):
        return "'" + s
    return s


def _day(value):
    try:
        day=date.fromisoformat(value)
    except (TypeError, ValueError) as exc:
        raise ValueError("Research date must be YYYY-MM-DD") from exc
    if day > date.today():
        raise ValueError("Future research date unsupported")
    return day.isoformat()


def build_review_packet(data):
    if not isinstance(data,dict) or set(data)!={"project_id","run_id","date_local","candidates"}:
        raise ValueError("Research packet requires exact project_id/run_id/date_local/candidates keys")
    if data["project_id"] != PROJECT_ID:
        raise ValueError("Personal career project identity mismatch")
    rid=_text(data["run_id"],"run_id",limit=100)
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]{2,99}",rid):
        raise ValueError("Invalid run identifier")
    run_day=_day(data["date_local"])
    people=data["candidates"]
    if not isinstance(people,list) or not 0<=len(people)<=MAX_PEOPLE:
        raise ValueError("Accept only up to 20 source research candidates")
    seen=set()
    rows=[]
    held=0
    for item in people:
        if not isinstance(item,dict) or not set(item).issubset(ALLOWED) or item.get("project_id")!=PROJECT_ID:
            raise ValueError("Unrecognized or cross-project research field")
        reasons=scope_reasons(item,require_project_id=True)
        if reasons:
            raise ValueError("Career purpose HOLD: "+",".join(reasons))
        name=_text(item.get("person_name"),"person_name",limit=240)
        org=_text(item.get("organization"),"organization",limit=240)
        role=_text(item.get("current_title"),"current_title",limit=240)
        reason=_text(item.get("why_connect"),"why_connect",limit=500)
        if len(reason)<25 or len(name.split())<2:
            raise ValueError("Research candidate needs real name and specific career rationale")
        norm=" ".join(name.casefold().split())
        if norm in seen:
            raise ValueError("Duplicate or possible namesake in the same run; resolve manually")
        seen.add(norm)
        segment=item.get("segment","other")
        category=item.get("category","unknown")
        route_type=item.get("route_type","NO_ROUTE")
        if segment not in SEGMENTS or category not in CATEGORIES or route_type not in ROUTES:
            raise ValueError("Invalid segment, category or route type")
        role_url=_url(item.get("role_source_url"),"role_source_url")
        reason_url=_url(item.get("reason_source_url"),"reason_source_url")
        route_url=_url(item.get("route_url"),"route_url")
        profile=_url(item.get("profile_url"),"profile_url")
        if route_type!="NO_ROUTE" and not route_url:
            raise ValueError("Public professional route needs an evidenced URL")
        observed=_day(item.get("observed_on")) if item.get("observed_on") else ""
        score=item.get("score_total")
        if score is not None and (isinstance(score,bool) or not isinstance(score,(int,float)) or not 0<=score<=100):
            raise ValueError("Invalid provisional scoring value")
        # Provisional ID is NOT a private person identifier nor proof of uniqueness.
        pid="RESEARCH-"+hashlib.sha256((norm+"|"+(profile or role_url)).encode()).hexdigest()[:16].upper()
        evidence="PENDING_REVIEW" if (role_url and reason_url and observed) else "HOLD"
        held+=int(evidence=="HOLD")
        rows.append([
            pid,name,org,role,{"tucson":"Tucson / Southern AZ","remote":"US Remote","other":"Other / Needs Review"}[segment],
            {"hiring-influencer":"Hiring Influencer","strategic-connector":"Strategic Connector",
             "hiring-decision-maker":"Hiring Decision-Maker","unknown":"Unknown"}[category],
            reason,role_url,reason_url,observed,evidence,
            "UNCHECKED","UNVERIFIED",route_type,route_url,
            "" if score is None else score,"NOT_REVIEWED",run_day,rid
        ])
    run=[rid,run_day,"FADI PERSONAL CAREER / PUBLIC RESEARCH ONLY",len(rows),0,held,
         0,0,0,0,MAX_PEOPLE,"REVIEW_PENDING","",
         "UNSENT research; no private history checked. Provisional IDs; 0 contact-ready."]
    return {
        "prospects":[PROSPECT_HEADERS]+rows,
        "daily_runs":[RUN_HEADERS,run],
        "manifest":{
            "project_id":PROJECT_ID,"run_id":rid,"date_local":run_day,
            "people_considered":len(rows),"people_held_for_missing_public_evidence":held,
            "new_contact_ready":0,"messages_sent":0,"approval_granted":False,
            "private_history_checked":False,"codex_native_skill_activation_verified":False,
            "destination":"Fadi private Google Drive review ONLY",
            "provisional_ids_not_qualified_for_person_identity":True,
            "warning":"Import into Google Drive only after manually checking stable IDs/duplicates. "
                      "The tracker does not prove novelty, current roles, sender consent or skill activation."
        }
    }


def write_review_packet(data,output_dir:Path):
    """Create a new directory outside the PUBLIC repository; no overwrite."""
    root=Path(__file__).resolve().parents[1]
    target=Path(output_dir).expanduser().resolve()
    if target==root or root in target.parents:
        raise ValueError("Never store candidate packets inside the public Git checkout")
    if target.exists():
        raise FileExistsError("Choose an unused private output directory")
    packet=build_review_packet(data)  # Validate before changing filesystem.
    target.mkdir(parents=True,mode=0o700)
    for key,filename in (("prospects","prospects-review.csv"),("daily_runs","daily-run-review.csv")):
        with (target/filename).open("x",encoding="utf-8-sig",newline="") as fh:
            writer=csv.writer(fh)
            writer.writerows([[_csv_safe(x) for x in row] for row in packet[key]])
    # Feed the existing owner-ONLY protected memory batch checker with exact
    # ordered PUBLIC names/profiles. No private relationship data is included.
    public_candidates = [
        {key: person[key] for key in ("project_id","person_name","profile_url","why_connect")
         if key in person and person[key] is not None}
        for person in data["candidates"]
    ]
    names = [
        {key: person[key] for key in ("person_name","profile_url")
         if key in person and person[key] is not None}
        for person in public_candidates
    ]
    for filename, value in (("candidate-batch.json",names),
                            ("candidate-public-review.json",public_candidates)):
        with (target/filename).open("x",encoding="utf-8") as stream:
            json.dump(value,stream,ensure_ascii=False,indent=2)
            stream.write("\n")
    with (target/"manifest.json").open("x",encoding="utf-8") as fh:
        json.dump(packet["manifest"],fh,indent=2)
        fh.write("\n")
    return packet["manifest"]


def read_input(path):
    source=Path(path).expanduser().resolve()
    root=Path(__file__).resolve().parents[1]
    if source==root or root in source.parents:
        raise ValueError("Do not put research candidate files in public Git")
    if not source.is_file() or source.stat().st_size>MAX_BYTES:
        raise ValueError("Missing or oversized research packet")
    return json.loads(source.read_text(encoding="utf-8-sig"))
