"""Encryption, person-level dedup, consent and private-path controls."""
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from outreach_agent.state import PrivateStore, REPO
from outreach_agent.learning import summarize, propose_strategy

class MemoryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.store=PrivateStore(Path(self.tmp.name)/"contacts.sqlite",
                                key=Fernet.generate_key(),identity_key="b"*64)
        self.person={
            "person_name":"Completely Fictional Executive",
            "organization":"Imaginary Works",
            "profile_url":"https://imaginary-works.test/bio",
            "current_title":"Head of Product",
            "role_quote":"Completely Fictional Executive is Head of Product at Imaginary Works.",
            "second_role_quote":"Completely Fictional Executive is Head of Product at Imaginary Works.",
            "initiative_quote":"Imaginary Works is improving enterprise product workflows and digital platforms.",
            "source_url":"https://imaginary-works.test/team",
            "second_role_source_url":"https://fictional-event.test/speakers",
            "observed_on":"2026-10-28",
            "route_url":"https://imaginary-works.test/contact",
            "route_type":"INDIRECT",
            "route_note":"General company contact form; not a verified personal introduction.",
            "why_connect":"Discuss enterprise product strategy and platform modernization with leadership.",
            "segment":"tucson",
            "category":"strategic-connector",
            "scores":{"alignment":25,"influence":20,"conversation":18,"reachability":7,"geography":10},
            "score_total":80,
            "verified_evidence_grade":"TWO_DISTINCT_SOURCE_HOSTS",
            "draft_status":"PENDING_CONTENT_APPROVAL",
        }
    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_private_path_restriction(self):
        with self.assertRaises(ValueError):
            PrivateStore(REPO/"oops.db",key=Fernet.generate_key(),identity_key="b"*64)

    def test_fails_closed_without_keys(self):
        with self.assertRaises(RuntimeError):
            PrivateStore(Path(self.tmp.name)/"x.db",key=None,identity_key=None)

    def test_duplicate_employer_change_hold(self):
        pid=self.store.register(self.person,segment="tucson")
        new=dict(self.person, organization="Totally Different Firm")
        self.assertEqual(len(self.store.match(new)),1)
        with self.assertRaises(ValueError):
            self.store.register(new,segment="remote")
        self.assertTrue(pid)

    def test_nothing_sensitive_in_plaintext_database(self):
        self.store.register(self.person)
        binary=(Path(self.tmp.name)/"contacts.sqlite").read_bytes()
        self.assertNotIn(self.person["person_name"].encode(),binary)
        self.assertNotIn(self.person["organization"].encode(),binary)

    def test_draft_approval_separate_from_send_authorization(self):
        pid=self.store.register(self.person)
        draft="Hello, let's discuss platforms."
        with self.assertRaisesRegex(ValueError,"INDEPENDENT_REVIEW_NOT_RECORDED"):
            self.store.approval(pid,draft,"CONTENT_APPROVED")
        self.store.review_contact(pid,confirmed_role=True,
                                  confirmed_route=True,confirmed_fit=True)
        with self.assertRaises(ValueError):
            self.store.approval(pid,draft,"SEND_AUTHORIZED")
        sha=self.store.approval(pid,draft,"CONTENT_APPROVED")
        self.assertTrue(sha)
        with self.assertRaises(ValueError):
            self.store.approval(pid,draft+" changed","SEND_AUTHORIZED")
        self.assertEqual(self.store.approval(pid,draft,"SEND_AUTHORIZED"),sha)

    def test_real_contact_required_for_reply(self):
        pid=self.store.register(self.person)
        with self.assertRaises(ValueError):
            self.store.record_event(pid,"REPLIED")
        self.store.record_event(pid,"CONTACTED",{"observed":"manually"})
        self.store.record_event(pid,"REPLIED",{"observed":"manually"})
        counts=self.store.counts()
        self.assertEqual(sum(x["n"] for x in counts if x["kind"]=="REPLIED"),1)

    def test_per_run_contact_ready_count_requires_review_and_excludes_opt_out(self):
        self.store.start_run("synthetic-run")
        pid=self.store.register(self.person,run_id="synthetic-run")
        self.assertEqual(self.store.reviewed_for_run("synthetic-run"),0)
        self.store.review_contact(pid,confirmed_role=True,confirmed_route=True,confirmed_fit=True)
        self.assertEqual(self.store.reviewed_for_run("synthetic-run"),1)
        self.assertEqual(self.store.reviewed_for_run("nonexistent-run"),0)
        self.store.record_event(pid,"OPTED_OUT")
        self.assertEqual(self.store.reviewed_for_run("synthetic-run"),0)

    def test_opt_out_blocks_further_actions(self):
        pid=self.store.register(self.person)
        self.store.record_event(pid,"OPTED_OUT")
        with self.assertRaises(ValueError):
            self.store.record_event(pid,"CONTACTED")
        with self.assertRaises(ValueError):
            self.store.approval(pid,"hi","CONTENT_APPROVED")

    def test_learn_but_no_silent_weight_change(self):
        pid=self.store.register(self.person)
        self.store.record_event(pid,"CONTACTED")
        self.store.record_event(pid,"REPLIED")
        summary=summarize(self.store.counts())
        self.assertEqual(summary["weight_changes_applied"],0)
        self.assertEqual(summary["segments"][0]["replies"],1)
        self.assertIsNone(propose_strategy(self.store.counts())["proposed_priority"])

    def test_strategy_is_manual(self):
        self.assertEqual(self.store.get_strategy(),"tucson")
        self.store.set_strategy("remote")
        self.assertEqual(self.store.get_strategy(),"remote")
        with self.assertRaises(ValueError):
            self.store.set_strategy("only-healthcare")

if __name__=="__main__":
    unittest.main()
