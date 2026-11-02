"""V2.2 end-to-end structural handoff and schema/policy consistency checks."""
import copy
import json
import unittest
from datetime import date
from pathlib import Path

from outreach_agent.career_contribution import validate_v22_packet
from outreach_agent.career_intelligence import RESEARCH_STATES, ENGAGEMENT_STATES, DECISIONS
from scripts.assess_career_opportunities_v22 import assess_v22_packet
from test_career_contribution import fixture, pack


ROOT=Path(__file__).resolve().parents[1]


class V22IntegrationTests(unittest.TestCase):
    def test_policy_matches_evaluator_research_and_engagement_states(self):
        p=json.loads((ROOT/"config/operating-policy.json").read_text())
        c=p["career_intelligence"]
        self.assertEqual(set(c["research_states"]),RESEARCH_STATES)
        self.assertEqual(set(c["engagement_states"]),ENGAGEMENT_STATES)
        self.assertTrue(c["v22_candidate_hardening"]["enabled_for_production"] is False)

    def test_two_opportunities_for_same_employer_remain_distinct(self):
        x=fixture()
        y=copy.deepcopy(x)
        y["contribution"]["mandate_key"]="different-product-mandate"
        report=assess_v22_packet(pack([x,y]))
        self.assertEqual(report["reviewed"],2)
        self.assertNotEqual(report["assessments"][0]["opportunity_identity"],
                            report["assessments"][1]["opportunity_identity"])
        self.assertFalse(report["native_skills_verified"])
        self.assertEqual(report["contact_ready"],0)

    def test_duplicate_identity_held_without_silent_deletion(self):
        x=fixture()
        report=assess_v22_packet(pack([x,copy.deepcopy(x)]))
        self.assertEqual(report["reviewed"],2)
        self.assertTrue(all(x["research_state"]=="EVIDENCE_HOLD" for x in report["assessments"]))
        self.assertTrue(all("IDENTITY_COLLISION_HOLD" in x["reasons"] for x in report["assessments"]))

    def test_unrelated_commercial_project_id_rejected(self):
        x=fixture()
        x["purpose"]="Send our subcontracting proposal"
        result=assess_v22_packet(pack([x]))
        self.assertEqual(result["assessments"][0]["research_state"],"EXCLUDED")
        self.assertEqual(result["contact_ready"],0)

    def test_source_claim_lie_can_never_be_called_verified_by_runner(self):
        x=fixture()
        r=assess_v22_packet(pack([x]))
        self.assertFalse(r["source_truth_independently_verified"])
        self.assertEqual(r["stage_manifest"]["source_provenance"],
                         "SELF_REPORTED_NOT_INDEPENDENTLY_VERIFIED")

    def test_no_public_owner_approval_or_action(self):
        x=fixture()
        p=pack([x])
        p["private_notes"]="should never be in a public research packet"
        with self.assertRaises(ValueError):
            assess_v22_packet(p)

if __name__=="__main__":
    unittest.main()
