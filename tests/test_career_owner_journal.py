"""Owner journal adversarial tests with synthetic in-memory key only."""
import copy
import tempfile
import unittest
from pathlib import Path

from outreach_agent.career_owner_journal import (
    append_owner_preference, verify_owner_journal,
)
from outreach_agent.career_source_witness import digest, sign_witness
from scripts.assess_career_opportunities_v22 import assess_v22_packet
from test_career_contribution import pack, fixture

KEY=b"X"*32

def prepared():
    packet=pack([fixture()])
    report=assess_v22_packet(packet)
    observations=[
        {"index":i,"claim_id":claim["claim_id"],"url":claim["source_url"],
         "status":"HOST_NOT_APPROVED","source_sha256":None}
        for i,item in enumerate(packet["opportunities"]) for claim in item["claims"]
    ]
    receipt=sign_witness({
        "project_id":"PERSONAL_CAREER_OUTREACH","run_id":packet["run_id"],
        "packet_sha256":digest(packet), "results":observations,
        "all_source_text_reproduced":False,
        "source_truth_independently_verified":False,
    },KEY)
    return report,receipt


class OwnerJournalTests(unittest.TestCase):
    def test_explicit_preference_chained_and_persistent(self):
        report,receipt=prepared()
        with tempfile.TemporaryDirectory() as temp:
            kwargs={"report":report,"witness":receipt,"index":0,
                    "decision":"PURSUE","reason":"LEADERSHIP_SCOPE",
                    "memory_result":{"result":"NOT_FOUND_IN_LOCAL_STORE"},"consent":True}
            r=append_owner_preference(temp,KEY,**kwargs)
            self.assertEqual(r["decision_recorded"],"PURSUE")
            self.assertFalse(r["send_authorized"])
            self.assertEqual(verify_owner_journal(temp,KEY)["verified_events"],1)
            with self.assertRaises(ValueError):
                append_owner_preference(temp,KEY,**kwargs)
            self.assertEqual(verify_owner_journal(temp,KEY)["verified_events"],1)

    def test_changed_assessment_cannot_reuse_source_witness(self):
        report,receipt=prepared()
        report["assessments"][0]["research_state"]="ASSESSABLE_BUT_FABRICATED"
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_owner_preference(temp,KEY,report=report,witness=receipt,index=0,
                                        decision="PURSUE",reason="ROLE_MATCH",
                                        memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=True)

    def test_source_packet_replay_rejected(self):
        report,receipt=prepared()
        report["run_id"]="different-run"
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_owner_preference(temp,KEY,report=report,witness=receipt,index=0,
                                        decision="PURSUE",reason="ROLE_MATCH",
                                        memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=True)

    def test_missing_history_for_named_executive_fails_closed(self):
        report,receipt=prepared()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_owner_preference(temp,KEY,report=report,witness=receipt,index=0,
                                        decision="RESEARCH_MORE",reason="SOURCE_GAP",
                                        memory_result={"result":"NO_NAMED_EXECUTIVE"},consent=True)

    def test_missing_owner_consent_fails(self):
        report,receipt=prepared()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_owner_preference(temp,KEY,report=report,witness=receipt,index=0,
                                        decision="PURSUE",reason="ROLE_MATCH",
                                        memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=False)

    def test_modified_journal_detected_after_restart(self):
        report,receipt=prepared()
        with tempfile.TemporaryDirectory() as temp:
            append_owner_preference(temp,KEY,report=report,witness=receipt,index=0,
                                    decision="RESEARCH_MORE",reason="SOURCE_GAP",
                                    memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=True)
            journal=Path(temp)/"owner-reviews.jsonl"
            journal.write_text(journal.read_text().replace("SOURCE_GAP","ROLE_MATCH"))
            with self.assertRaises(ValueError):
                verify_owner_journal(temp,KEY)
            with self.assertRaises(ValueError):
                verify_owner_journal(temp,b"Z"*32)

    def test_signed_receipt_with_incomplete_claims_is_still_rejected(self):
        report,receipt=prepared()
        receipt["results"]=[]
        receipt=sign_witness(receipt,KEY)
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_owner_preference(temp,KEY,report=report,witness=receipt,index=0,
                                        decision="RESEARCH_MORE",reason="SOURCE_GAP",
                                        memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=True)

    def test_same_witness_other_key_does_not_pass(self):
        report,receipt=prepared()
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                append_owner_preference(temp,b"Z"*32,report=report,witness=receipt,index=0,
                                        decision="REJECT",reason="SOURCE_GAP",
                                        memory_result={"result":"NOT_FOUND_IN_LOCAL_STORE"},consent=True)

if __name__=="__main__":
    unittest.main()
