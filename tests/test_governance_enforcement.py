"""Deterministic governance denial and audit tests. All identities/sources synthetic."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from cryptography.fernet import Fernet
from outreach_agent.state import PrivateStore
from outreach_agent.governance import active_policy, structural_review_gate

def vetted_synthetic():
    return {
        "person_name":"Morgan Synthetic", "organization":"Fabricated Innovation",
        "current_title":"Head of Product",
        "role_quote":"Morgan Synthetic leads product at Fabricated Innovation.",
        "second_role_quote":"Morgan Synthetic leads product at Fabricated Innovation.",
        "initiative_quote":"Fabricated Innovation is modernizing enterprise product workflows.",
        "source_url":"https://fabricated-innovation.test/leadership",
        "second_role_source_url":"https://fictitious-conference.test/speaker",
        "route_url":"https://fabricated-innovation.test/contact",
        "route_type":"INDIRECT",
        "route_note":"Generic official company contact page, not a direct route.",
        "observed_on":"2026-10-28",
        "why_connect":"A substantive discussion of enterprise product strategy and AI adoption.",
        "segment":"tucson", "category":"strategic-connector",
        "scores":{"alignment":25,"influence":20,"conversation":18,
                  "reachability":7,"geography":10},
        "score_total":80,
        "verified_evidence_grade":"TWO_DISTINCT_SOURCE_HOSTS",
        "draft_status":"PENDING_CONTENT_APPROVAL"
    }

class EnforcementTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.path=Path(self.tmp.name)/"encrypted.sqlite"
        self.store=PrivateStore(self.path,key=Fernet.generate_key(),identity_key="k"*64)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_new_user_reported_entry_cannot_self_promote(self):
        self.store.remember_relationship("Already Seen", "FIRST_LEARNED")
        pid=self.store.match({"person_name":"Already Seen"})[0]["person_id"]
        with self.assertRaisesRegex(ValueError,"INSUFFICIENT_SOURCE_ROUTE_OR_SCORE_EVIDENCE"):
            self.store.review_contact(pid,confirmed_role=True,confirmed_route=True,
                                      confirmed_fit=True)
        with self.assertRaisesRegex(ValueError,"STRUCTURAL_GATE_NOT_PASSED"):
            self.store.approval(pid,"Hello", "CONTENT_APPROVED")
        self.assertEqual(self.store.human_reviewed_count(),0)
        audit=self.store.recent_governance_decisions()
        self.assertEqual([r["decision"] for r in audit], ["HOLD","HOLD"])
        self.assertTrue(all(r["policy_version"]=="0.2.0" for r in audit))

    def test_approval_requires_separate_review_and_exact_draft_hash(self):
        pid=self.store.register(vetted_synthetic())
        with self.assertRaisesRegex(ValueError,"INDEPENDENT_REVIEW_NOT_RECORDED"):
            self.store.approval(pid,"Hello", "CONTENT_APPROVED")
        self.store.review_contact(pid,confirmed_role=True,confirmed_route=True,
                                  confirmed_fit=True)
        with self.assertRaisesRegex(ValueError,"EXACT_DRAFT_CONTENT_NOT_APPROVED"):
            self.store.approval(pid,"Hello", "SEND_AUTHORIZED")
        sha=self.store.approval(pid,"Hello","CONTENT_APPROVED")
        with self.assertRaisesRegex(ValueError,"EXACT_DRAFT_CONTENT_NOT_APPROVED"):
            self.store.approval(pid,"Modified", "SEND_AUTHORIZED")
        self.assertEqual(sha,self.store.approval(pid,"Hello","SEND_AUTHORIZED"))
        audit=self.store.recent_governance_decisions()
        self.assertEqual(audit[0]["decision"],"ALLOW_APPROVAL_RECORD")
        self.assertTrue(all("Hello" not in str(r) for r in audit))
        self.assertTrue(all(r["policy_version"]=="0.2.0" for r in audit))

    def test_rejected_unverified_and_existing_people(self):
        poor=vetted_synthetic()
        del poor["second_role_source_url"]
        self.assertEqual(structural_review_gate(poor,opted_out=False)["decision"],"HOLD")
        known=vetted_synthetic()
        known["user_relationship_status"]="PREVIOUSLY_MET"
        decision=structural_review_gate(known,opted_out=False)
        self.assertEqual(decision["decision"],"HOLD")
        self.assertIn("EXISTING_RELATIONSHIP_NOT_NEW",decision["reasons"])

    def test_optout_blocks_after_review_and_is_audited(self):
        pid=self.store.register(vetted_synthetic())
        self.store.review_contact(pid,confirmed_role=True,confirmed_route=True,
                                  confirmed_fit=True)
        self.store.record_event(pid,"OPTED_OUT")
        with self.assertRaisesRegex(ValueError,"SUPPRESSED_IDENTITY"):
            self.store.approval(pid,"Hello","CONTENT_APPROVED")
        self.assertIn("SUPPRESSED_IDENTITY",
                      self.store.recent_governance_decisions()[0]["reason_codes"])

    def test_disabled_policy_fails_closed(self):
        policy=active_policy()
        with tempfile.TemporaryDirectory() as d:
            f=Path(d)/"policy.json"
            policy["outreach"]["automatic_sending"]=True
            f.write_text(json.dumps(policy),encoding="utf-8")
            with patch("outreach_agent.governance.POLICY_PATH",f):
                with self.assertRaisesRegex(RuntimeError,"fail closed"):
                    active_policy()
                pid=self.store.register(vetted_synthetic())
                with self.assertRaisesRegex(RuntimeError,"fail closed"):
                    self.store.review_contact(pid,confirmed_role=True,
                                              confirmed_route=True,confirmed_fit=True)

if __name__=="__main__":
    unittest.main()
