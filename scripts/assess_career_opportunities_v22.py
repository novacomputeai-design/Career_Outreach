"""Supervised V2.2 public-source CLAIM preflight and optional private continuity.

No browser, Codex host, DPAPI, approval, mail, application or sender. A PASS
means source-claim structure ONLY; it never means source truth or contact-ready.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path

from outreach_agent.career_contribution import validate_v22_packet, evaluate_v22_opportunity
from outreach_agent.career_intelligence import opportunity_identity
from outreach_agent.career_intelligence_packet import MAX_PACKET_BYTES, _safe_public
from outreach_agent.career_run_ledger import record_run_snapshot
from outreach_agent.career_handoff import audit_research_handoffs

ROOT = Path(__file__).resolve().parents[1]


def safe_private_path(path):
    out = Path(path).expanduser().resolve()
    if out == ROOT or ROOT in out.parents:
        raise ValueError("PUBLIC_REPO_PATH_FORBIDDEN")
    if out.suffix.lower() != ".json":
        raise ValueError("JSON_ONLY")
    return out


def assess_v22_packet(packet):
    validate_v22_packet(packet)
    _safe_public(packet)
    d = date.fromisoformat(packet["date_local"])
    if d > date.today():
        raise ValueError("FUTURE_RUN_DATE")
    findings, seen = [], {}
    for index, record in enumerate(packet["opportunities"]):
        assessment = evaluate_v22_opportunity(record)
        projected = dict(record)
        projected["schema_version"] = "2.1"
        projected.pop("career_value", None)
        identity, problem = opportunity_identity(projected)
        if problem:
            assessment["reasons"] = sorted(set(assessment["reasons"]+[problem]))
            assessment["research_state"] = "EVIDENCE_HOLD"
            assessment["engagement_readiness"] = "NOT_PREPARED"
        assessment["opportunity_identity"] = identity
        findings.append(assessment)
        if identity is not None:
            seen.setdefault(identity, []).append(index)
    for positions in seen.values():
        if len(positions)>1:
            for index in positions:
                f = findings[index]
                f["reasons"] = sorted(set(f["reasons"]+["IDENTITY_COLLISION_HOLD"]))
                f["research_state"] = "EVIDENCE_HOLD"
                f["engagement_readiness"] = "NOT_PREPARED"
    return {
        "schema_version":"2.2", "project_id":"PERSONAL_CAREER_OUTREACH",
        "run_id":packet["run_id"], "date_local":packet["date_local"],
        "reviewed":len(findings), "opportunity_records":packet["opportunities"],
        "assessments":findings,
        "stage_manifest":{
            "organization_research":"HOST_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
            "source_provenance":"SELF_REPORTED_NOT_INDEPENDENTLY_VERIFIED",
            "contribution_and_timing":"STRUCTURALLY_ASSESSED",
            "executive_and_route":"STRUCTURALLY_ASSESSED",
            "opportunity_evaluator":"REPOSITORY_CODE_EXECUTED",
            "owner_memory":"NOT_ACCESSED",
            "owner_review":"NOT_AUTHENTICATED",
            "native_skill_invocation":"NOT_VERIFIED",
            "outbound_actions":"NOT_AUTHORIZED",
        },
        "source_truth_independently_verified":False,
        "native_skills_verified":False, "private_history_checked":False,
        "owner_decisions_authenticated":False,
        "contact_ready":0, "send_authorized":False, "outbound_sent":0,
        "applications_submitted":0,
        "status":"RESEARCH_STRUCTURAL_REVIEW_NOT_FULL_E2E",
    }


def main():
    parser=argparse.ArgumentParser(description="V2.2 bounded research preflight; NOT E2E production")
    parser.add_argument("--input",required=True)
    parser.add_argument("--out",required=True)
    parser.add_argument("--history-dir",help="user-owned public-claims-only immutable run history; optional")
    parser.add_argument("--host-trace",help="optional untrusted stage handoff digest-chain JSON; NOT host attestation")
    args=parser.parse_args()
    src,dst=safe_private_path(args.input),safe_private_path(args.out)
    if src==dst or dst.exists():
        raise ValueError("OUTPUT_MUST_BE_NEW_FILE")
    if not src.is_file() or src.stat().st_size>MAX_PACKET_BYTES:
        raise ValueError("INPUT_MISSING_OR_OVERSIZED")
    packet=json.loads(src.read_text(encoding="utf-8-sig"))
    report=assess_v22_packet(packet)
    if args.host_trace:
        trace_path=safe_private_path(args.host_trace)
        if not trace_path.is_file() or trace_path.stat().st_size>MAX_PACKET_BYTES:
            raise ValueError("HOST_TRACE_NOT_FOUND_OR_OVERSIZED")
        trace=json.loads(trace_path.read_text(encoding="utf-8-sig"))
        report["handoff_audit"]=audit_research_handoffs(trace)
    if args.history_dir:
        snapshot=record_run_snapshot(
            args.history_dir,run_id=packet["run_id"],date_local=packet["date_local"],
            opportunity_records=packet["opportunities"],assessments=report["assessments"])
        report["opportunity_continuity"]=snapshot["continuity"]
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open("x",encoding="utf-8") as f:
        json.dump(report,f,ensure_ascii=False,indent=2)
        f.write("\n")
    print("V2.2 STRUCTURAL RESEARCH ONLY:",report["reviewed"],"records")
    print("SOURCE_TRUTH NOT VERIFIED; NATIVE SKILLS NOT VERIFIED; CONTACT_READY 0; SENT 0")


if __name__=="__main__":
    main()
