"""Private user-reported relationship classification. Synthetic identities only."""
import tempfile
import unittest
from pathlib import Path
from cryptography.fernet import Fernet
from outreach_agent.state import PrivateStore

class UserRelationshipTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name) / "relationships.sqlite"
        self.key = Fernet.generate_key()
        self.identity_key = "u" * 64
        self.store = PrivateStore(self.path, key=self.key, identity_key=self.identity_key)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_first_learned_is_not_contact_ready_or_outreach(self):
        result = self.store.remember_relationship(
            "Avery Example", "FIRST_LEARNED",
            profile_url="https://fictional-university.test/people/avery-example")
        self.assertEqual(result["result"], "RECORDED")
        self.assertFalse(result["granted_contact_readiness"])
        self.assertEqual(result["messages_sent"], 0)
        check = self.store.check_relationship("avery   example")
        self.assertEqual(check["result"], "SEEN_IN_STORE")
        self.assertEqual(check["user_reported_relationship"], "FIRST_LEARNED")
        self.assertEqual(check["novelty"], "ALREADY_IN_LOCAL_STORE")
        self.assertEqual(self.store.human_reviewed_count(), 0)
        self.assertEqual(self.store.counts()[0]["kind"], "USER_REPORTED_RELATIONSHIP")
        self.assertNotIn(b"Avery Example", self.path.read_bytes())

    def test_known_person_not_counted_as_new(self):
        r = self.store.remember_relationship("Jordan Sample", "PREVIOUSLY_MET")
        self.assertEqual(r["relationship"], "PREVIOUSLY_MET")
        check = self.store.check_relationship("Jordan Sample")
        self.assertEqual(check["result"], "EXISTING_RELATIONSHIP")
        self.assertEqual(check["user_reported_relationship"], "PREVIOUSLY_MET")
        self.assertFalse(check["suppressed"])

    def test_unknown_name_is_not_proof_of_novelty(self):
        r = self.store.check_relationship("Unknown Example")
        self.assertEqual(r["result"], "NOT_FOUND_IN_LOCAL_STORE")
        self.assertEqual(r["novelty"], "UNVERIFIED")

    def test_repeat_is_idempotent_and_conflicting_report_holds(self):
        self.store.remember_relationship("Taylor Synthetic", "FIRST_LEARNED")
        r = self.store.remember_relationship("Taylor Synthetic", "FIRST_LEARNED")
        self.assertEqual(r["result"], "ALREADY_RECORDED")
        self.assertEqual(sum(x["n"] for x in self.store.counts()
                             if x["kind"] == "USER_REPORTED_RELATIONSHIP"), 1)
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            self.store.remember_relationship("Taylor Synthetic", "PREVIOUSLY_MET")

    def test_profile_disagreement_holds_namesake(self):
        self.store.remember_relationship(
            "Taylor Duplicate", "FIRST_LEARNED",
            profile_url="https://example.test/one")
        with self.assertRaisesRegex(ValueError, "different-profile"):
            self.store.remember_relationship(
                "Taylor Duplicate", "FIRST_LEARNED",
                profile_url="https://example.test/two")
        check = self.store.check_relationship("Taylor Duplicate",
                                              profile_url="https://example.test/two")
        self.assertEqual(check["result"], "POSSIBLE_NAMESAKE_HOLD")

    def test_existing_recommendation_can_be_classified_without_recontact(self):
        person = {"person_name": "Avery Stored",
                  "profile_url": "https://imaginary-org.test/avery",
                  "organization": "Imaginary Org"}
        pid = self.store.register(person)
        r = self.store.remember_relationship("Avery Stored", "PREVIOUSLY_MET")
        self.assertEqual(r["result"], "UPDATED_EXISTING_RECORD")
        self.assertEqual(self.store.check_relationship("Avery Stored")["result"],
                         "EXISTING_RELATIONSHIP")
        counts = self.store.counts()
        self.assertFalse(any(x["kind"] == "CONTACTED" for x in counts))
        self.assertTrue(pid)

    def test_prior_contact_conflicts_with_first_learned(self):
        pid = self.store.register({"person_name": "Prior Contact"})
        self.store.record_event(pid, "CONTACTED")
        with self.assertRaisesRegex(ValueError, "Recorded prior outreach"):
            self.store.remember_relationship("Prior Contact", "FIRST_LEARNED")

    def test_opt_out_cannot_be_cleared(self):
        pid = self.store.register({"person_name": "Opted Out"})
        self.store.record_event(pid, "OPTED_OUT")
        with self.assertRaisesRegex(ValueError, "Suppressed"):
            self.store.remember_relationship("Opted Out", "FIRST_LEARNED")
        self.assertTrue(self.store.check_relationship("Opted Out")["suppressed"])

    def test_persists_across_database_connections(self):
        self.store.remember_relationship("Persistent Example", "PREVIOUSLY_MET")
        self.store.close()
        self.store = PrivateStore(self.path, key=self.key, identity_key=self.identity_key)
        self.assertEqual(self.store.check_relationship("Persistent Example")[
            "user_reported_relationship"], "PREVIOUSLY_MET")

    def test_invalid_identity_rejected(self):
        with self.assertRaises(ValueError):
            self.store.remember_relationship("Avery", "FIRST_LEARNED")
        with self.assertRaises(ValueError):
            self.store.remember_relationship("Avery Example", "INVALID")
        self.assertEqual(self.store.check_relationship("Avery Example")[
            "result"], "NOT_FOUND_IN_LOCAL_STORE")


    def test_read_only_lookup_preserves_state(self):
        self.store.remember_relationship("Example Leader", "PREVIOUSLY_MET")
        self.store.close()
        self.store = PrivateStore(self.path, key=self.key, identity_key=self.identity_key)
        store = PrivateStore(self.path, key=self.key, identity_key=self.identity_key,
                             read_only=True)
        try:
            check = store.check_relationship("Example Leader")
            self.assertEqual(check["result"], "EXISTING_RELATIONSHIP")
            with self.assertRaises(Exception):
                store.remember_relationship("Another Example", "FIRST_LEARNED")
        finally:
            store.close()
        self.assertEqual(self.store.check_relationship("Another Example")["result"],
                         "NOT_FOUND_IN_LOCAL_STORE")

    def test_read_only_missing_database_fails_closed(self):
        with self.assertRaises(FileNotFoundError):
            PrivateStore(Path(self.tmp.name) / "missing.sqlite",
                         key=self.key, identity_key=self.identity_key, read_only=True)
        self.assertFalse((Path(self.tmp.name) / "missing.sqlite").exists())

if __name__ == "__main__":
    unittest.main()
