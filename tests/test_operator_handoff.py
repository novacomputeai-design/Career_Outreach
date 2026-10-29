"""Synthetic tests for operator-controlled DPAPI-free candidate reconciliation."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from cryptography.fernet import Fernet
from outreach_agent.memory_batch import screen_batch
from outreach_agent.operator_handoff import reconcile_operator_screening
from outreach_agent.project_scope import PROJECT_ID
from outreach_agent.state import PrivateStore


class OperatorHandoffTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.store = PrivateStore(
            self.root / "synthetic-memory.sqlite",
            key=Fernet.generate_key(),
            identity_key="a" * 64,
        )
        self.store.remember_relationship(
            "Jordan Example", "PREVIOUSLY_MET",
            profile_url="https://synthetic.test/jordan",
        )
        self.candidates = [
            {"project_id": PROJECT_ID, "person_name":"Jordan Example",
             "profile_url":"https://synthetic.test/jordan",
             "why_connect":"Explore enterprise platform operating models."},
            {"project_id": PROJECT_ID, "person_name":"Avery Example",
             "why_connect":"Discuss enterprise product modernization strategy."},
        ]
        self.input = self.root / "candidate-batch.json"
        self.input.write_text(json.dumps([
            {"person_name":"Jordan Example","profile_url":"https://synthetic.test/jordan"},
            {"person_name":"Avery Example"},
        ]), encoding="utf-8")
        self.response = screen_batch(self.store, self.input)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def test_exact_batch_reconciliation_never_confers_new_or_send_authority(self):
        result = reconcile_operator_screening(self.candidates, self.response)
        self.assertEqual(result["project_id"], PROJECT_ID)
        self.assertEqual(result["people_reconciled"], 2)
        self.assertEqual(result["new_contact_ready"], 0)
        self.assertFalse(result["complete_cross_channel_history_verified"])
        self.assertFalse(result["operator_identity_authenticated"])
        self.assertFalse(result["send_authorized"])
        self.assertEqual(result["classifications"][0]["operator_review_queue"],
                         "EXISTING_FOLLOW_UP_NOT_NEW")
        self.assertEqual(result["classifications"][1]["operator_review_queue"],
                         "NOVELTY_UNVERIFIED_HOLD")
        self.assertTrue(all(not x["contact_ready"] for x in result["classifications"]))
        self.assertNotIn("state_key", str(result))
        self.assertNotIn("PREVIOUSLY_MET", str(result))

    def test_reordered_names_do_not_bind_to_old_batch(self):
        with self.assertRaisesRegex(ValueError, "Screening does not match"):
            reconcile_operator_screening(self.candidates[::-1], self.response)

    def test_changed_public_profile_detected(self):
        changed = [dict(x) for x in self.candidates]
        changed[0]["profile_url"] = "https://synthetic.test/different-person"
        with self.assertRaisesRegex(ValueError, "Screening does not match"):
            reconcile_operator_screening(changed, self.response)

    def test_forged_novelty_claim_fails_closed(self):
        response = dict(self.response)
        response["results"] = [dict(x) for x in self.response["results"]]
        response["results"][1]["novelty"] = "NEW"
        with self.assertRaisesRegex(ValueError, "classification"):
            reconcile_operator_screening(self.candidates, response)

    def test_wrong_screening_metadata_is_rejected(self):
        response = dict(self.response, new_contact_ready_granted=1)
        with self.assertRaisesRegex(ValueError,"assurance"):
            reconcile_operator_screening(self.candidates, response)
        response = dict(self.response, verification_level="AGENT_CERTIFIED_NEW")
        with self.assertRaisesRegex(ValueError,"assurance"):
            reconcile_operator_screening(self.candidates, response)

    def test_cross_project_candidate_rejected_even_if_batch_matches(self):
        wrong = [dict(x) for x in self.candidates]
        wrong[1]["why_connect"] = "Submit our capability statement for a federal task order"
        with self.assertRaisesRegex(ValueError, "scope gate"):
            reconcile_operator_screening(wrong, self.response)
        wrong[1] = dict(self.candidates[1], project_id="NOVA_SUBCONTRACTING")
        with self.assertRaisesRegex(ValueError, "scope gate"):
            reconcile_operator_screening(wrong, self.response)

    def test_identity_suppression_is_a_hold(self):
        p = self.store.match({"person_name":"Jordan Example"})[0]["person_id"]
        self.store.record_event(p, "OPTED_OUT")
        response = screen_batch(self.store, self.input)
        result = reconcile_operator_screening(self.candidates, response)
        self.assertEqual(result["classifications"][0]["operator_review_queue"],
                         "SUPPRESSED_HOLD")
        self.assertEqual(result["new_contact_ready"], 0)

    def test_mismatch_and_duplicate_inputs_hold(self):
        duplicate = [self.candidates[0], dict(self.candidates[0])]
        with self.assertRaisesRegex(ValueError, "Duplicate names"):
            reconcile_operator_screening(duplicate, self.response)
        truncated = dict(self.response, results=self.response["results"][:1])
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            reconcile_operator_screening(self.candidates, truncated)


if __name__ == "__main__":
    unittest.main()
