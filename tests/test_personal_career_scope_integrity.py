"""P0 adversarial personal-career isolation and durable identity integrity tests.

All records are synthetic. No user secrets, sends, or live Windows database.
"""
import sqlite3
from contextlib import closing
import tempfile
import unittest
from pathlib import Path

from cryptography.fernet import Fernet
from outreach_agent.governance import structural_review_gate
from outreach_agent.project_scope import PROJECT_ID, scope_reasons
from outreach_agent.state import PrivateStore


class PersonalCareerBoundaryTests(unittest.TestCase):
    def test_federal_capture_object_not_a_career_prospect(self):
        wrong = {
            "project_id": "NOVA_SUBCONTRACTING",
            "prime_contractor": "Fictitious Federal Prime",
            "award_piid": "SYNTHETIC-AWARD",
            "why_connect": "Seek a subcontracting teaming opportunity for Nova Compute services",
            "person_name": "Morgan Example",
        }
        reasons = scope_reasons(wrong, require_project_id=True)
        self.assertIn("PROJECT_ID_MISMATCH", reasons)
        self.assertIn("CROSS_PROJECT_BUSINESS_CAPTURE_FIELDS", reasons)
        self.assertIn("CROSS_PROJECT_COMMERCIAL_OUTREACH_INTENT", reasons)
        result = structural_review_gate(wrong, opted_out=False)
        self.assertEqual(result["decision"], "HOLD")
        self.assertFalse(result["contact_ready"])
        self.assertIn("PROJECT_ID_MISMATCH", result["reasons"])

    def test_commercial_purpose_with_spoofed_career_id_still_holds(self):
        wrong = {"project_id": PROJECT_ID, "purpose": "BUSINESS_DEVELOPMENT",
                 "why_connect": "Ask this prime contractor about subcontracting"}
        reasons = scope_reasons(wrong, require_project_id=True)
        self.assertIn("COMMERCIAL_PURPOSE_NOT_PERSONAL_CAREER", reasons)
        self.assertIn("CROSS_PROJECT_COMMERCIAL_OUTREACH_INTENT", reasons)

    def test_disguised_supplier_message_with_career_id_holds(self):
        for rationale in (
            "Send our capability statement to the prime's vendor onboarding team.",
            "Offer our AI services to support the awarded contract.",
            "Pursue a government task order for our company.",
            "Nova Compute would provide technical solutions to the supplier team.",
        ):
            with self.subTest(rationale=rationale):
                record={"project_id":PROJECT_ID,"person_name":"Avery Example",
                        "why_connect":rationale,"purpose":"career_networking"}
                self.assertIn("CROSS_PROJECT_COMMERCIAL_OUTREACH_INTENT",
                              scope_reasons(record, require_project_id=True))

    def test_career_conversation_with_government_employer_stays_eligible(self):
        record={"project_id":PROJECT_ID,
                "organization":"Fabricated Government Contractor",
                "why_connect":"Discuss enterprise product leadership with the COO.",
                "purpose":"individual_career_networking"}
        self.assertEqual(scope_reasons(record, require_project_id=True), [])

    def test_missing_project_id_never_pretends_to_be_qualified(self):
        self.assertIn("PROJECT_ID_NOT_VERIFIED",
                      scope_reasons({"person_name": "Taylor Example"}, require_project_id=True))

    def test_legitimate_government_employer_not_automatically_excluded(self):
        record = {"project_id":PROJECT_ID, "organization":"Synthetic Government Contractor",
                  "why_connect":"Discuss a personal career in enterprise product leadership"}
        self.assertEqual(scope_reasons(record, require_project_id=True), [])


class ExistingMemoryIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.path = Path(self.temp.name) / "synthetic-memory.sqlite"
        self.state_key = Fernet.generate_key()
        self.identity_key = "m"*64
        store = PrivateStore(self.path,key=self.state_key,identity_key=self.identity_key)
        store.remember_relationship("Avery Synthetic", "PREVIOUSLY_MET",
                                    profile_url="https://synthetic-company.test/avery")
        store.close()

    def tearDown(self):
        self.temp.cleanup()

    def test_wrong_identity_key_cannot_hide_existing_person(self):
        with self.assertRaisesRegex(RuntimeError, "identity key mismatch"):
            PrivateStore(self.path,key=self.state_key,identity_key="x"*64,
                         read_only=True)
        with self.assertRaisesRegex(RuntimeError, "identity key mismatch"):
            PrivateStore(self.path,key=self.state_key,identity_key="x"*64)
        correct = PrivateStore(self.path,key=self.state_key,identity_key=self.identity_key,
                               read_only=True)
        try:
            self.assertEqual(correct.check_relationship("Avery Synthetic")["result"],
                             "EXISTING_RELATIONSHIP")
        finally:
            correct.close()

    def test_wrong_state_key_fails_even_with_correct_identity_key(self):
        with self.assertRaisesRegex(RuntimeError, "Cannot authenticate private record"):
            PrivateStore(self.path,key=Fernet.generate_key(),
                         identity_key=self.identity_key,read_only=True)

    def test_profile_hmac_tamper_fails_closed(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("UPDATE people SET profile_digest=?",
                       ("e"*64,))
            db.commit()
        with self.assertRaisesRegex(RuntimeError, "identity key/profile mismatch"):
            PrivateStore(self.path,key=self.state_key,
                         identity_key=self.identity_key,read_only=True)

    def test_legacy_database_open_read_only_but_never_implicitly_migrates(self):
        with closing(sqlite3.connect(self.path)) as db:
            db.execute("DROP TABLE governance_decisions")
        source = PrivateStore(self.path,key=self.state_key,
                              identity_key=self.identity_key,read_only=True)
        try:
            self.assertEqual(source.verify_identity_binding(),1)
        finally:
            source.close()
        with self.assertRaisesRegex(RuntimeError, "explicit owner-approved schema migration"):
            PrivateStore(self.path,key=self.state_key,identity_key=self.identity_key)
        with closing(sqlite3.connect(self.path)) as db:
            self.assertIsNone(db.execute(
                "SELECT name FROM sqlite_master WHERE name='governance_decisions'").fetchone())

    def test_cross_project_object_cannot_enter_memory(self):
        store = PrivateStore(self.path,key=self.state_key,identity_key=self.identity_key)
        try:
            with self.assertRaisesRegex(ValueError, "Personal career scope HOLD"):
                store.register({"person_name":"Different Synthetic",
                                "project_id":"NOVA_SUBCONTRACTING",
                                "award_piid":"SYNTHETIC"})
        finally:
            store.close()


if __name__ == "__main__":
    unittest.main()
