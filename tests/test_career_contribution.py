"""Negative and positive V2.2 contribution quality tests (synthetic only)."""
import copy
import unittest
from datetime import date, timedelta
from jsonschema import ValidationError

from outreach_agent.career_contribution import (
    assess_contribution, evaluate_v22_opportunity, validate_v22_packet,
)
from test_career_intelligence import sample, claim


def fixture():
    x = sample(executive=True)
    x["schema_version"] = "2.2"
    x["career_value"] = {
        "business_decision": "Determine which enterprise AI products create measurable operational value",
        "proposed_internal_responsibility": "Lead the business-facing AI product portfolio and cross-functional adoption",
        "candidate_evidence_refs": ["MOBIUS_PRODUCT_PORTFOLIO", "MOBIUS_AI_PRIORITIZATION"],
        "complementary_scope": "Own product prioritization and adoption without replacing existing AI engineering",
        "existing_owner_status": "OWNER_RESEARCHED_NOT_FOUND",
        "expected_outcome": "Improve measurable adoption and business value across enterprise product workflows",
        "limitations": "No demonstrated clinical or utility-specific qualifications",
        "trigger_claim_id": "trigger",
        "maturity": "DEPLOYED",
    }
    x["claims"].append(claim("trigger", "BUSINESS_TRIGGER",
                             "The employer announced expansion of its AI program."))
    return x


def pack(items):
    return {
        "schema_version": "2.2", "project_id": "PERSONAL_CAREER_OUTREACH",
        "run_id": "synthetic-v22-001", "date_local": date.today().isoformat(),
        "opportunities": items,
    }


class ContributionMasteryTests(unittest.TestCase):
    def test_01_strong_is_only_source_reported_hypothesis(self):
        x = fixture()
        validate_v22_packet(pack([x]))
        a = evaluate_v22_opportunity(x)
        self.assertEqual(a["career_value_assessment"]["contribution_quality"], "STRONG_CONTRIBUTION")
        self.assertEqual(a["career_value_assessment"]["timing_status"], "RESEARCH_NOW")
        self.assertFalse(a["source_truth_independently_verified"])
        self.assertFalse(a["contact_ready"])
        self.assertFalse(a["send_authorized"])

    def test_02_unknown_product_owner_downgrades_research(self):
        x = fixture()
        x["career_value"]["existing_owner_status"] = "OWNER_UNKNOWN"
        a = evaluate_v22_opportunity(x)
        self.assertEqual(a["career_value_assessment"]["contribution_quality"], "CONTRIBUTION_RESEARCH_NEEDED")
        self.assertEqual(a["engagement_readiness"], "RESEARCH_PENDING")

    def test_03_old_trigger_not_engage_now(self):
        x = fixture()
        x["claims"][-1]["published_on"] = (date.today()-timedelta(days=300)).isoformat()
        self.assertEqual(assess_contribution(x)["timing_status"], "MONITOR_TRIGGER")

    def test_04_unverified_trigger_not_engage_now(self):
        x = fixture()
        x["claims"][-1]["page_read_success"] = False
        self.assertEqual(assess_contribution(x)["timing_status"], "NO_TIMING_BASIS")

    def test_05_fake_candidate_capability_rejected(self):
        x = fixture()
        x["career_value"]["candidate_evidence_refs"] = ["NOT_IN_APPROVED_PROFILE"]
        with self.assertRaises(ValueError):
            validate_v22_packet(pack([x]))

    def test_06_incomplete_claim_cannot_pass_schema(self):
        x = fixture()
        del x["claims"][0]["source_origin_id"]
        with self.assertRaises(ValueError):
            validate_v22_packet(pack([x]))

    def test_07_random_private_or_unsafe_field_rejected(self):
        x = fixture()
        x["career_value"]["private_email"] = "private@example.test"
        with self.assertRaises(ValueError):
            validate_v22_packet(pack([x]))

    def test_08_cross_project_rejected(self):
        x = fixture()
        x["project_id"] = "NOVA_SUBCONTRACTING"
        with self.assertRaises(ValueError):
            validate_v22_packet(pack([x]))

    def test_09_direct_hiring_retains_independent_ats_preflight(self):
        x = fixture()
        y = sample("DIRECT_HIRING")
        y["schema_version"] = "2.2"
        y["career_value"] = copy.deepcopy(x["career_value"])
        # No verified business objective is required by the verified direct ATS path.
        r = evaluate_v22_opportunity(y)
        self.assertEqual(r["hiring_evidence"], "ACTIVE_POSTED_ROLE")
        self.assertFalse(r["contact_ready"])
        self.assertFalse(r["send_authorized"])

    def test_10_no_permission_even_if_executive_route_is_supplied(self):
        x = fixture()
        a = evaluate_v22_opportunity(x)
        self.assertEqual(a["engagement_readiness"], "ENGAGEMENT_REVIEW_ELIGIBLE")
        self.assertFalse(a["contact_ready"])

if __name__ == "__main__":
    unittest.main()
