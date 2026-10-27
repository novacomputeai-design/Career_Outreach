"""Operator CLI; no automatic external message sending."""
import argparse
import json
import os
from pathlib import Path
from .state import PrivateStore
from .pipeline import make_brief
from .learning import summarize, propose_strategy
from .research import Tavily, Extractor, SEARCH_QUERIES, BoundedSearch, BoundedExtractor

ROOT=Path(__file__).resolve().parents[1]
def private_path(path):
    p=Path(path).expanduser().resolve()
    if p==ROOT or ROOT in p.parents:
        raise ValueError("Private files must be outside public repository")
    return p

def emit(data, outfile=None):
    payload=json.dumps(data, ensure_ascii=False, indent=2)+"\n"
    if outfile:
        p=private_path(outfile)
        p.parent.mkdir(parents=True,exist_ok=True,mode=0o700)
        p.write_text(payload,encoding="utf-8")
        if os.name=="posix":
            p.chmod(0o600)
    else:
        print(payload)

def main(argv=None):
    p=argparse.ArgumentParser(description="Personal Executive Outreach — research only, never automatic sending")
    p.add_argument("--db",default=os.getenv("OUTREACH_DB_PATH"))
    sub=p.add_subparsers(dest="command",required=True)
    run=sub.add_parser("run")
    run.add_argument("--out",required=True)
    run.add_argument("--target",type=int,default=20)
    run.add_argument("--max-queries",type=int,default=14)
    run.add_argument("--max-enrich",type=int,default=48)
    run.add_argument("--max-search-calls",type=int,default=50)
    run.add_argument("--max-extractions",type=int,default=40)
    record=sub.add_parser("record")
    record.add_argument("--person-id",required=True)
    record.add_argument("--event",required=True)
    record.add_argument("--note",default="")
    approve=sub.add_parser("approve")
    approve.add_argument("--person-id",required=True)
    approve.add_argument("--draft-file",required=True)
    approve.add_argument("--stage",choices=["CONTENT_APPROVED","SEND_AUTHORIZED"],required=True)
    review=sub.add_parser("review-contact",help="Explicit human source and route review; never sends")
    review.add_argument("--person-id",required=True)
    review.add_argument("--confirm-current-role",action="store_true",required=True)
    review.add_argument("--confirm-contact-route",action="store_true",required=True)
    review.add_argument("--confirm-professional-relevance",action="store_true",required=True)
    sub.add_parser("learning")
    restore=sub.add_parser("restore-report",help="Recover latest encrypted run after an output-file failure")
    restore.add_argument("--out",required=True)
    strat=sub.add_parser("approve-strategy")
    strat.add_argument("--segment",choices=["tucson","remote"],required=True)
    args=p.parse_args(argv)
    if not args.db:
        p.error("Set OUTREACH_DB_PATH or --db")
    if args.command=="run" and not (1<=args.target<=20 and 1<=args.max_queries<=40 and 1<=args.max_enrich<=100):
        p.error("Limits: target 1..20, max queries 1..40, max enrich 1..100")
    if args.command=="run":
        # Fail before creating a new database if required provider keys are absent.
        if not os.getenv("TAVILY_API_KEY") or not os.getenv("OPENAI_API_KEY"):
            p.error("Live provider keys unavailable; no autonomous research run possible")
    store=PrivateStore(private_path(args.db))
    try:
        if args.command=="run":
            q=list(SEARCH_QUERIES)
            if store.get_strategy()=="remote":
                q.sort(key=lambda x: (0 if "remote" in x.lower() else 1))
            search=BoundedSearch(Tavily(),max_calls=args.max_search_calls)
            extractor=BoundedExtractor(Extractor(),max_calls=args.max_extractions)
            result=make_brief(search,extractor,store,target=args.target,
                              max_queries=args.max_queries,max_enrich=args.max_enrich,queries=q)
            emit(result,args.out)
            emit({"run_id":result["run_id"],"provisionally_source_corroborated":result["source_corroborated_pending_human_review"],
                  "human_reviewed_contact_ready":result["new_contact_ready"],
                  "shortfall":result["shortfall"],"messages_sent":0,"audit_level":result["audit_status"]})
            if result["stage"]=="PARTIAL_SOURCE_FAILURE":
                raise SystemExit("Source coverage failed; report preserved privately for operator review")
        elif args.command=="record":
            store.record_event(args.person_id,args.event,{"note":args.note})
            emit({"event_recorded":args.event,"message_sent_by_agent":False})
        elif args.command=="approve":
            content=private_path(args.draft_file).read_text(encoding="utf-8")
            emit({"draft_sha256":store.approval(args.person_id,content,args.stage),
                  "approval_stage":args.stage,"message_sent_by_agent":False})
        elif args.command=="restore-report":
            saved=store.latest_report()
            if saved is None:
                raise RuntimeError("No completed private run is available to restore")
            emit(saved,args.out)
            emit({"restored":True,"run_id":saved.get("run_id"),"messages_sent":0})
        elif args.command=="review-contact":
            store.review_contact(args.person_id, confirmed_role=args.confirm_current_role,
                                 confirmed_route=args.confirm_contact_route,
                                 confirmed_fit=args.confirm_professional_relevance)
            emit({"person_id":args.person_id,"human_review_confirmed":True,
                  "message_sent_by_agent":False})
        elif args.command=="learning":
            counts=store.counts()
            data=summarize(counts)
            data["proposed_strategy"]=propose_strategy(counts)
            data["approved_strategy"]=store.get_strategy()
            emit(data)
        elif args.command=="approve-strategy":
            store.set_strategy(args.segment)
            emit({"approved_priority":args.segment,"automatic_weight_change":False})
    finally:
        store.close()

if __name__=="__main__":
    main()
