"""Private-folder-only synthetic cross-run continuity tests."""
import copy
import tempfile
import unittest
from datetime import date
from pathlib import Path

from outreach_agent.career_run_ledger import (
    build_reconciliation, record_run_snapshot, read_latest_continuity,
)
from outreach_agent.career_intelligence import evaluate_opportunity
from test_career_intelligence import sample


def direct(requisition):
    x = sample("DIRECT_HIRING")
    x["job"]["requisition_id"] = requisition
    x["claims"][-1]["object_id"] = requisition
    return x


class LedgerTests(unittest.TestCase):
    def test_optum_two_requisitions_survive_next_run(self):
        with tempfile.TemporaryDirectory() as work:
            root = Path(work) / "private-run-history"
            a, b = direct("2389532"), direct("2379061")
            out1 = record_run_snapshot(root, run_id="research-001", date_local=date.today().isoformat(),
                                       opportunity_records=[a, b],
                                       assessments=[evaluate_opportunity(a), evaluate_opportunity(b)])
            out2 = record_run_snapshot(root, run_id="research-002", date_local=date.today().isoformat(),
                                       opportunity_records=[b], assessments=[evaluate_opportunity(b)])
            self.assertEqual(len(out1["continuity"]), 2)
            self.assertEqual(len(out2["continuity"]), 2)
            a2 = next(x for x in out2["continuity"] if "2389532" in x["identity_key"])
            self.assertEqual(a2["current_run_observation"], "NOT_OBSERVED_THIS_RUN")
            self.assertEqual(a2["last_seen_run"], "research-001")
            self.assertEqual(len(read_latest_continuity(root)), 2)
            self.assertFalse(a2["actionable_now"])

    def test_same_run_id_is_idempotent(self):
        with tempfile.TemporaryDirectory() as work:
            x = sample()
            kwargs = {"run_id": "research-001", "date_local": date.today().isoformat(),
                      "opportunity_records": [x], "assessments": [evaluate_opportunity(x)]}
            record_run_snapshot(work, **kwargs)
            same = record_run_snapshot(work, **kwargs)
            self.assertEqual(len(same["continuity"]), 1)

    def test_conflicting_replay_fails(self):
        with tempfile.TemporaryDirectory() as work:
            x=sample(); k={"run_id": "research-001","date_local": date.today().isoformat()}
            record_run_snapshot(work,**k,opportunity_records=[x],assessments=[evaluate_opportunity(x)])
            y=copy.deepcopy(x);y["initiative"]["initiative_id"]="other"
            with self.assertRaises(FileExistsError):
                record_run_snapshot(work,**k,opportunity_records=[y],assessments=[evaluate_opportunity(y)])

    def test_duplicate_opportunities_cannot_be_written(self):
        x=sample()
        with self.assertRaises(ValueError):
            build_reconciliation([],run_id="dup-001",date_local=date.today().isoformat(),
                                 opportunity_records=[x,x],
                                 assessments=[evaluate_opportunity(x),evaluate_opportunity(x)])

    def test_owner_decision_cannot_be_smuggled_into_public_ledger(self):
        x=sample();o=evaluate_opportunity(x);o["owner_decision"]="PURSUE"
        with self.assertRaises(ValueError):
            build_reconciliation([],run_id="audit-001",date_local=date.today().isoformat(),
                                 opportunity_records=[x],assessments=[o])

    def test_read_only_never_creates_files(self):
        with tempfile.TemporaryDirectory() as work:
            p=Path(work)/"not-created"
            self.assertEqual(read_latest_continuity(p),[])
            self.assertFalse(p.exists())

    def test_research_cannot_authorize_contact(self):
        x=sample();o=evaluate_opportunity(x);o["contact_ready"]=True
        with self.assertRaises(ValueError):
            build_reconciliation([],run_id="audit-002",date_local=date.today().isoformat(),
                                 opportunity_records=[x],assessments=[o])

if __name__=="__main__":
    unittest.main()
