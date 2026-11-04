"""V2.2 E2E-37: output-state policy, evaluator, schema contract parity.

The research packet schema intentionally contains INPUT claims only.
The separate OUTPUT schema enumerates assessment states and gates.
This proves deterministic policy/shape alignment, not live truth.
"""
import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from outreach_agent.career_intelligence import RESEARCH_STATES, ENGAGEMENT_STATES
from scripts.assess_career_opportunities_v22 import assess_v22_packet
from test_career_contribution import fixture, pack

ROOT = Path(__file__).resolve().parents[1]


class V22AssessmentOutputStateContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads(
            (ROOT / "schemas" / "career-assessment-v2.2-output.schema.json").read_text(encoding="utf-8")
        )
        cls.policy = json.loads(
            (ROOT / "config" / "operating-policy.json").read_text(encoding="utf-8")
        )["career_intelligence"]
        Draft202012Validator.check_schema(cls.schema)

    def test_e2e_37_policy_evaluator_and_output_schema_match(self):
        assessment = self.schema["properties"]["assessments"]["items"]["properties"]
        self.assertEqual(set(assessment["research_state"]["enum"]),
                         set(self.policy["research_states"]))
        self.assertEqual(set(assessment["research_state"]["enum"]), RESEARCH_STATES)
        self.assertEqual(set(assessment["engagement_readiness"]["enum"]),
                         set(self.policy["engagement_states"]))
        self.assertEqual(set(assessment["engagement_readiness"]["enum"]), ENGAGEMENT_STATES)

    def test_actual_structural_report_validates_output_contract(self):
        p = pack([fixture()])
        report = assess_v22_packet(p)
        Draft202012Validator(self.schema).validate(report)
        self.assertEqual(report["source_truth_independently_verified"], False)
        self.assertEqual(report["contact_ready"], 0)
        self.assertEqual(report["send_authorized"], False)

    def test_output_schema_rejects_unknown_research_and_engagement_states(self):
        report = assess_v22_packet(pack([fixture()]))
        for field, value in (("research_state", "APPROVED_FOR_CONTACT"),
                             ("engagement_readiness", "SEND_AUTHORIZED")):
            invalid = copy.deepcopy(report)
            invalid["assessments"][0][field] = value
            self.assertFalse(Draft202012Validator(self.schema).is_valid(invalid))

    def test_output_schema_rejects_unearned_authentication_or_contact(self):
        report = assess_v22_packet(pack([fixture()]))
        for field, value in (("source_truth_independently_verified", True),
                             ("native_skills_verified", True),
                             ("contact_ready", 1),
                             ("send_authorized", True)):
            invalid = copy.deepcopy(report)
            invalid[field] = value
            self.assertFalse(Draft202012Validator(self.schema).is_valid(invalid))


if __name__ == "__main__":
    unittest.main()
