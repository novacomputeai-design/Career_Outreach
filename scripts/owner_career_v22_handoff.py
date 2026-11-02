"""Owner-Windows-only trusted boundary for V2.2 public evidence and decisions.

Must be launched from an interactive user PowerShell session after DPAPI unlock.
Codex never calls this process or receives keys. Research review != send approval.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import sys

from outreach_agent.career_source_witness import (
    witness_sources, sign_witness, digest,
)
from outreach_agent.career_owner_journal import (
    append_owner_preference, validate_owner_handoff, verify_owner_journal,
    propose_verified_owner_learning,
)
from outreach_agent.career_contribution import validate_v22_packet
from outreach_agent.state import PrivateStore

ROOT=Path(__file__).resolve().parents[1]


def private_file(path, *, existing):
    if os.name != "nt" or not os.environ.get("LOCALAPPDATA"):
        raise RuntimeError("TRUSTED_OWNER_WINDOWS_ONLY")
    base=(Path(os.environ["LOCALAPPDATA"])/"CareerOutreach").resolve()
    p=Path(path).expanduser().resolve()
    if base not in p.parents or p == base or p == ROOT or ROOT in p.parents:
        raise ValueError("OWNER_FILE_OUTSIDE_PRIVATE_WINDOWS_FOLDER")
    if p.suffix != ".json" or p.is_symlink() or (existing and not p.is_file()):
        raise ValueError("INVALID_PRIVATE_JSON_FILE")
    if existing and p.stat().st_size > 2 * 1024 * 1024:
        raise ValueError("PRIVATE_FILE_TOO_LARGE")
    if not existing and p.exists():
        raise FileExistsError("NEVER_OVERWRITE_TRUSTED_OUTPUT")
    return p


def read_json(path):
    return json.loads(private_file(path, existing=True).read_text(encoding="utf-8-sig"))


def write_new(path, data):
    dst=private_file(path,existing=False)
    dst.parent.mkdir(parents=True,exist_ok=True)
    with dst.open("x",encoding="utf-8") as stream:
        json.dump(data,stream,sort_keys=True,ensure_ascii=False,indent=2)
        stream.write("\n")


def main():
    parser=argparse.ArgumentParser(description="Owner-only V2.2 research witness and reviewed preference")
    sub=parser.add_subparsers(dest="mode",required=True)
    source=sub.add_parser("source-witness")
    source.add_argument("--packet",required=True)
    source.add_argument("--out",required=True)
    source.add_argument("--allow-host",action="append",required=True)
    review=sub.add_parser("owner-review")
    review.add_argument("--report",required=True)
    review.add_argument("--witness",required=True)
    review.add_argument("--index",required=True,type=int)
    review.add_argument("--decision",required=True,choices=["PURSUE","RESEARCH_MORE","REJECT"])
    review.add_argument("--reason",required=True)
    verify=sub.add_parser("verify-journal")
    learning=sub.add_parser("learning-proposals")
    args=parser.parse_args()

    if os.name != "nt" or not sys.stdin.isatty():
        raise RuntimeError("INTERACTIVE_OWNER_WINDOWS_CONSOLE_REQUIRED")
    if not os.getenv("OUTREACH_STATE_KEY") or not os.getenv("OUTREACH_IDENTITY_KEY"):
        raise RuntimeError("DPAPI_PROTECTED_OWNER_KEYS_NOT_AVAILABLE")
    root=Path(os.environ["LOCALAPPDATA"])/"CareerOutreach"
    db=root/"relationships.sqlite"
    store=PrivateStore(db,read_only=True)
    try:
        secret=store.identity_key
        if args.mode == "source-witness":
            packet=read_json(args.packet)
            validate_v22_packet(packet)
            print("SOURCE WITNESS: public web only. Approved hosts:",", ".join(args.allow_host))
            token=packet["run_id"][-8:]
            entered=input("Type FETCH "+token+" to authorize bounded read: ").strip()
            if entered!="FETCH "+token:
                raise ValueError("SOURCE_FETCH_NOT_OWNER_CONFIRMED")
            receipt=sign_witness(witness_sources(packet,args.allow_host),secret)
            write_new(args.out,receipt)
            print(json.dumps({
                "receipt_written":True,"claims_checked":len(receipt["results"]),
                "all_source_text_reproduced":receipt["all_source_text_reproduced"],
                "semantic_truth_proven":False,"contact_ready":False,"send_authorized":False
            }))
        elif args.mode == "owner-review":
            report=read_json(args.report)
            witness=read_json(args.witness)
            record, assessment, report_hash, _=validate_owner_handoff(
                report,witness,secret,args.index)
            executive=record.get("executive")
            if executive:
                status=store.check_relationship(executive["name"])
                # A namesake check without a verified profile is not proof of novelty.
                memory_result={"result":status["result"]}
            else:
                memory_result={"result":"NO_NAMED_EXECUTIVE"}
            print("REVIEW TARGET:",record["organization"]["name"])
            print("PROPOSED RESPONSIBILITY:",record["career_value"]["proposed_internal_responsibility"])
            print("RESEARCH:",assessment["research_state"],
                  " | WITNESSED ALL TEXT:",witness.get("all_source_text_reproduced"))
            print("PRIVATE LOCAL HISTORY:",memory_result["result"])
            print("This records research interest ONLY. It never permits outreach or applications.")
            phrase="REVIEW "+report_hash[:10]
            if input("Type "+phrase+" to record this exact decision: ").strip()!=phrase:
                raise ValueError("OWNER_REVIEW_NOT_CONFIRMED")
            result=append_owner_preference(root/"owner-v22",secret,report=report,
                witness=witness,index=args.index,decision=args.decision,reason=args.reason,
                memory_result=memory_result,consent=True)
            print(json.dumps(result,sort_keys=True))
        elif args.mode == "verify-journal":
            print(json.dumps(verify_owner_journal(root/"owner-v22",secret)))
        elif args.mode == "learning-proposals":
            print(json.dumps(propose_verified_owner_learning(root/"owner-v22",secret)))
    finally:
        store.close()


if __name__=="__main__":
    main()
