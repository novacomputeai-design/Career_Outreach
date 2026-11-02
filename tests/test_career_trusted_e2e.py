"""Synthetic integration exercise of the exact public/owner boundary, not field proof."""
import tempfile
import unittest
from datetime import date
from pathlib import Path

from outreach_agent.career_source_witness import witness_sources, sign_witness, digest
from outreach_agent.career_run_ledger import record_run_snapshot, read_latest_continuity
from outreach_agent.career_owner_journal import (
    append_owner_preference, verify_owner_journal, propose_verified_owner_learning,
)
from scripts.assess_career_opportunities_v22 import assess_v22_packet
from test_career_contribution import pack, fixture


KEY=b"v22-synthetic-tests-key-only-not-live"*2
PUBLIC=lambda host,port,**kw: [(2,1,0,"",("93.184.216.34",443))]


class TrustedHandoffIntegratedTests(unittest.TestCase):
    def test_source_packet_to_owner_memory_assessment_learning_no_send(self):
        p=pack([fixture()])
        report=assess_v22_packet(p)
        webpages={}
        for c in p["opportunities"][0]["claims"]:
            old=webpages.get(c["source_url"], ("", "text/plain"))[0]
            webpages[c["source_url"]]=(old+" "+c["excerpt"],"text/plain")
        receipt=sign_witness(witness_sources(
            p,{"employer.example"},fetch=lambda url:webpages[url],resolver=PUBLIC),KEY)
        self.assertTrue(receipt["all_source_text_reproduced"])
        self.assertFalse(receipt["source_truth_independently_verified"])
        with tempfile.TemporaryDirectory() as work:
            root=Path(work)
            snapshot=record_run_snapshot(root/"public-claims",run_id=p["run_id"],
                date_local=p["date_local"],opportunity_records=p["opportunities"],
                assessments=report["assessments"])
            self.assertEqual(len(snapshot["continuity"]),1)
            decision=append_owner_preference(root/"owner-journal",KEY,
                report=report,witness=receipt,index=0,decision="PURSUE",
                reason="LEADERSHIP_SCOPE",memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},
                consent=True)
            self.assertEqual(decision["decision_recorded"],"PURSUE")
            self.assertFalse(decision["send_authorized"])
            self.assertEqual(verify_owner_journal(root/"owner-journal",KEY)["verified_events"],1)
            self.assertEqual(propose_verified_owner_learning(
                root/"owner-journal",KEY)["status"],"INSUFFICIENT_OWNER_REVIEWS")
            self.assertFalse(report["source_truth_independently_verified"])
            self.assertEqual(report["contact_ready"],0)
            self.assertFalse(snapshot["send_authorized"])
            self.assertFalse(read_latest_continuity(root/"public-claims")[0]["actionable_now"])

    def test_one_missing_source_does_not_become_verified_truth_or_send(self):
        p=pack([fixture()])
        report=assess_v22_packet(p)
        witness=sign_witness(witness_sources(
            p,{"unrelated.example"},fetch=lambda u:("Never fetch","text/plain"),
            resolver=PUBLIC),KEY)
        self.assertFalse(witness["all_source_text_reproduced"])
        with tempfile.TemporaryDirectory() as work:
            result=append_owner_preference(work,KEY,report=report,witness=witness,
                index=0,decision="RESEARCH_MORE",reason="SOURCE_GAP",
                memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=True)
            self.assertFalse(result["source_text_all_reproduced"])
            self.assertFalse(result["contact_ready"])
            self.assertFalse(result["send_authorized"])

if __name__=="__main__":
    unittest.main()
