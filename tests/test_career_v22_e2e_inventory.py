"""Adversarial E2E coverage inventory never self-certifies a test."""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class AdversarialInventoryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data=json.loads((ROOT/"evals/career_v22_e2e_matrix.json").read_text(encoding="utf-8"))

    def test_54_unique_semantically_named_cases(self):
        cases=self.data["cases"]
        self.assertEqual(len(cases),54)
        self.assertEqual(self.data["total"],54)
        self.assertEqual(len({x["name"] for x in cases}),54)
        self.assertTrue(all(not any(c.isdigit() for c in x["name"]) for x in cases))

    def test_no_e2e_case_can_be_paper_passed(self):
        self.assertTrue(all(x["execution_status"]=="NOT_RUN" for x in self.data["cases"]))
        self.assertTrue(all(not x["live_host_qualified"] for x in self.data["cases"]))
        self.assertTrue(all(not x["owner_approval_authorized"] for x in self.data["cases"]))

    def test_all_four_domains_present(self):
        from collections import Counter
        counts=Counter(x["area"] for x in self.data["cases"])
        self.assertEqual(set(counts),{"DISCOVERY_CONTRIBUTION","SOURCE_EXECUTIVE_TRUTH",
                                      "CONTINUITY_HIRING_REVIEW","SAFETY_MEMORY_RELIABILITY"})
        self.assertEqual(sorted(counts.values()),[11,11,16,16])

if __name__=="__main__":
    unittest.main()
