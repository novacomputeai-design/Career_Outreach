import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from qualify_candidates import evaluate, build_brief

def candidate(**changes):
    c = {
        "person_id": "synthetic-person-1",
        "person_name": "Example Executive",
        "organization": "Example Organization",
        "current_title": "Vice President, Product",
        "role_source_url": "https://example.org/team",
        "reason_source_url": "https://example.org/initiatives",
        "contact_route_url": "https://example.org/contact",
        "why_connect": "Discuss enterprise platform strategy with an experienced product leader.",
        "route_type": "INDIRECT",
        "role_verified": True,
        "contact_route_verified": True,
        "history_checked": True,
        "novelty": "NEW",
        "suppressed": False,
        "observed_on": "2026-10-27",
        "scores": {"alignment": 25, "influence": 20, "conversation": 18, "reachability": 12, "geography": 8}
    }
    c.update(changes)
    return c

class CandidateGateTests(unittest.TestCase):
    def test_valid_synthetic_candidate_passes_structure(self):
        ok, score, _ = evaluate(candidate(), set())
        self.assertTrue(ok)
        self.assertEqual(score, 83)
    def test_duplicate_previous_day(self):
        ok, _, errors = evaluate(candidate(), {"synthetic-person-1"})
        self.assertFalse(ok)
        self.assertIn("duplicate_person", errors)
    def test_duplicate_in_same_run(self):
        report = build_brief([candidate(), candidate()], set())
        self.assertEqual(report["contact_ready_pending_independent_evidence_audit"], 1)
    def test_guessed_or_missing_route_is_not_ready(self):
        ok, _, errors = evaluate(candidate(contact_route_verified=False), set())
        self.assertFalse(ok)
        self.assertIn("required_gate_contact_route_verified", errors)
    def test_missing_private_history_check(self):
        ok, _, errors = evaluate(candidate(history_checked=False), set())
        self.assertFalse(ok)
        self.assertIn("required_gate_history_checked", errors)
    def test_opt_out_suppression(self):
        ok, _, errors = evaluate(candidate(suppressed=True), set())
        self.assertFalse(ok)
        self.assertIn("suppressed_or_unconfirmed", errors)
    def test_under_threshold(self):
        c = candidate(scores={"alignment":10,"influence":10,"conversation":10,"reachability":10,"geography":9})
        self.assertFalse(evaluate(c, set())[0])
    def test_over_maximum_subscore(self):
        c = candidate(scores={"alignment":31,"influence":20,"conversation":15,"reachability":15,"geography":10})
        self.assertFalse(evaluate(c, set())[0])
    def test_fake_placeholder_url(self):
        self.assertFalse(evaluate(candidate(contact_route_url="not-a-real-url"), set())[0])
    def test_no_fabricated_quota_completion(self):
        report=build_brief([candidate()], set())
        self.assertEqual(report["shortfall"],19)
        self.assertEqual(report["messages_sent"],0)
        self.assertEqual(report["verification_level"],"STRUCTURAL_ONLY")
    def test_old_known_contact_not_new(self):
        self.assertFalse(evaluate(candidate(novelty="EXISTING"),set())[0])
    def test_remote_not_rejected_by_industry_or_hq(self):
        c=candidate(location_priority=2,organization="Synthetic Remote Manufacturer")
        self.assertTrue(evaluate(c,set())[0])

if __name__=="__main__":
    unittest.main()
