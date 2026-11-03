"""Narrow E2E-02/03/11/16 false-positive regressions via V2.2 CLI.

These tests prove deterministic CLI behavior on synthetic packets only. They
DO NOT execute native Codex skills, verify source truth, or grant contact.
"""
import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from test_career_contribution import fixture, pack

ROOT = Path(__file__).resolve().parents[1]


class CareerValueFalsePositiveCLITests(unittest.TestCase):
    def _cli_assessment(self, record):
        with tempfile.TemporaryDirectory(prefix="career-v22-fp-") as tmp:
            incoming = Path(tmp) / "source-packet.json"
            outgoing = Path(tmp) / "assessment.json"
            incoming.write_text(json.dumps(pack([record])), encoding="utf-8")
            call = subprocess.run(
                [sys.executable, "-m", "scripts.assess_career_opportunities_v22",
                 "--input", str(incoming), "--out", str(outgoing)],
                cwd=ROOT, capture_output=True, text=True,
            )
            self.assertEqual(call.returncode, 0, call.stderr)
            return json.loads(outgoing.read_text(encoding="utf-8"))["assessments"][0]

    def test_e2e_02_buzzword_without_operational_problem_cannot_be_strong(self):
        item = fixture()
        item["career_value"]["business_decision"] = (
            "Develop a transformative AI strategy that leverages synergistic innovation"
        )
        item["career_value"].pop("problem_claim_id")
        finding = self._cli_assessment(item)
        self.assertEqual(finding["career_value_assessment"]["contribution_quality"],
                         "CONTRIBUTION_RESEARCH_NEEDED")
        self.assertIn("OPERATIONAL_PROBLEM_NOT_DIRECTLY_SOURCE_LINKED",
                      finding["career_value_assessment"]["reason_codes"])
        self.assertFalse(finding["contact_ready"])

    def test_e2e_03_prestige_without_outcome_measure_cannot_be_strong(self):
        item = fixture()
        item["organization"]["name"] = "Prominent Prestigious Employer"
        item["career_value"]["expected_outcome"] = (
            "Join this influential employer and contribute to its excellent reputation."
        )
        item["career_value"].pop("outcome_metric")
        finding = self._cli_assessment(item)
        self.assertEqual(finding["career_value_assessment"]["contribution_quality"],
                         "CONTRIBUTION_RESEARCH_NEEDED")
        self.assertIn("MEASURABLE_OUTCOME_NOT_SPECIFIED",
                      finding["career_value_assessment"]["reason_codes"])

    def test_e2e_11_generic_strategy_without_bounded_scope_cannot_be_strong(self):
        item = fixture()
        item["career_value"]["proposed_internal_responsibility"] = (
            "Advise the organization on general artificial intelligence strategy"
        )
        item["career_value"]["mandate_boundary"] = "REQUIRES_SCOPE_REVIEW"
        finding = self._cli_assessment(item)
        self.assertEqual(finding["career_value_assessment"]["contribution_quality"],
                         "CONTRIBUTION_RESEARCH_NEEDED")
        self.assertIn("COMPLEMENTARY_MANDATE_NOT_ESTABLISHED",
                      finding["career_value_assessment"]["reason_codes"])

    def test_e2e_16_chief_function_takeover_is_not_credible_contribution(self):
        item = fixture()
        item["career_value"]["existing_owner_status"] = "EXISTING_OWNER_DOCUMENTED"
        item["career_value"]["mandate_boundary"] = "REPLACES_EXISTING_CHIEF_FUNCTION"
        finding = self._cli_assessment(item)
        self.assertEqual(finding["career_value_assessment"]["contribution_quality"],
                         "NO_CREDIBLE_CONTRIBUTION")
        self.assertEqual(finding["research_state"], "EVIDENCE_HOLD")
        self.assertIn("EXISTING_CHIEF_FUNCTION_TAKEOVER",
                      finding["career_value_assessment"]["reason_codes"])

    def test_existing_owner_even_when_complementarity_self_claimed_needs_review(self):
        item = fixture()
        item["career_value"]["existing_owner_status"] = "EXISTING_OWNER_DOCUMENTED"
        finding = self._cli_assessment(item)
        self.assertEqual(finding["career_value_assessment"]["contribution_quality"],
                         "CONTRIBUTION_RESEARCH_NEEDED")

    def test_positive_bounded_hypothesis_survives_without_proving_value(self):
        finding = self._cli_assessment(fixture())
        assessment = finding["career_value_assessment"]
        self.assertEqual(assessment["contribution_quality"], "STRONG_CONTRIBUTION")
        self.assertFalse(assessment["career_value_proven"])
        self.assertEqual(assessment["independent_semantic_review"], "NOT_PERFORMED")
        self.assertFalse(finding["source_truth_independently_verified"])
        self.assertFalse(finding["send_authorized"])

    def test_wrong_initiative_problem_claim_does_not_promote(self):
        item = fixture()
        problem = next(c for c in item["claims"] if c["claim_id"] == "operational-problem")
        problem["object_id"] = "some-other-initiative"
        finding = self._cli_assessment(item)
        self.assertEqual(finding["career_value_assessment"]["contribution_quality"],
                         "CONTRIBUTION_RESEARCH_NEEDED")

    def test_direct_hiring_keeps_independent_ats_and_does_not_auto_apply(self):
        from test_career_intelligence import sample
        item = sample("DIRECT_HIRING")
        item["schema_version"] = "2.2"
        item["career_value"] = copy.deepcopy(fixture()["career_value"])
        finding = self._cli_assessment(item)
        self.assertEqual(finding["hiring_evidence"], "ACTIVE_POSTED_ROLE")
        self.assertFalse(finding["application_submitted"])
        self.assertFalse(finding["send_authorized"])


if __name__ == "__main__":
    unittest.main()
