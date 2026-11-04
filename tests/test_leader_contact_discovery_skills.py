"""Focused read-only leader/contact skill-contract tests (not live Codex behavior).

These tests keep the five refined specialist instructions, V2.2 packet shape,
and example evaluation cases consistent. They do NOT attest email deliverability,
external source truth, owner memory, or native Codex activation.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = ROOT / ".agents" / "skills"
BRIEF = ROOT / "references" / "leader-contact-discovery-brief.md"
EVALS = ROOT / "evals" / "leader_contact_discovery_quality_cases.json"


class LeaderContactDiscoverySkillTests(unittest.TestCase):
    def setUp(self):
        self.skill = {
            name: (SKILL_ROOT / name / "SKILL.md").read_text(encoding="utf-8")
            for name in ("daily-executive-outreach", "leadership-discovery",
                         "contact-verification", "daily-executive-brief",
                         "run-quality-audit")
        }
        self.brief = BRIEF.read_text(encoding="utf-8")
        self.cases = json.loads(EVALS.read_text(encoding="utf-8"))

    def test_all_five_skills_stay_focused_on_sourced_people_and_contact_routes(self):
        self.assertIn("Focused read-only leader-discovery mode",
                      self.skill["daily-executive-outreach"])
        self.assertIn("Select the right person for a conversation",
                      self.skill["leadership-discovery"])
        self.assertIn("Bounded professional contact-finding procedure",
                      self.skill["contact-verification"])
        self.assertIn("Leader/contact shortlist", self.skill["daily-executive-brief"])
        self.assertIn("Contact-shortlist acceptance audit",
                      self.skill["run-quality-audit"])
        for name in ("daily-executive-outreach", "daily-executive-brief"):
            self.assertIn("leader-contact-discovery-brief.md", self.skill[name])
        self.assertIn("No owner-memory access", self.skill["daily-executive-outreach"])
        self.assertIn("not CONTACT_READY", self.skill["contact-verification"])

    def test_contact_classes_and_report_buckets_are_non_authoritative(self):
        for key in ("LISTED_WORK_EMAIL", "LISTED_OFFICE_PHONE",
                    "VERIFIED_PERSON_SPECIFIC_FORM", "INDIVIDUAL_PROFILE_IDENTIFIED",
                    "INDIRECT_GENERAL", "NONE"):
            self.assertIn(key, self.brief)
        for key in ("PERSON_ROUTE_SUPPORTED", "PROFILE_ONLY", "CONTACT_HOLD"):
            self.assertIn(key, self.brief)
            self.assertIn(key, self.skill["run-quality-audit"])
        self.assertIn("NOT", self.brief)
        self.assertIn("SEND_AUTHORIZED", self.brief)
        self.assertIn("outside PUBLIC Git", self.brief)
        self.assertIn("never a verified person-specific route", self.skill["contact-verification"])

    def test_v22_route_schema_unchanged_and_separated_from_display_only_contacts(self):
        schema = json.loads(
            (ROOT / "schemas" / "career-opportunity-v2.2.schema.json").read_text(encoding="utf-8")
        )
        route = schema["$defs"]["route"]
        self.assertEqual(set(route["properties"]),
                         {"route_type", "verified_for_person", "url"})
        self.assertFalse(route["additionalProperties"])
        self.assertIn("display-only", self.brief)
        policy = json.loads(
            (ROOT / "config" / "operating-policy.json").read_text(encoding="utf-8")
        )["career_intelligence"]
        self.assertIs(policy["safety"]["send_authorized"], False)
        self.assertIs(policy["safety"]["contact_ready_from_research"], False)
        self.assertIs(policy["v22_candidate_hardening"]["enabled_for_production"], False)

    def test_six_adversarial_examples_cover_expected_buckets_without_fake_passes(self):
        self.assertEqual(self.cases["assurance"], "UNEXECUTED_TEST_SCENARIOS")
        rows = self.cases["cases"]
        self.assertEqual(len(rows), 6)
        self.assertEqual(len({row["name"] for row in rows}), len(rows))
        expected = {
            "official_named_work_email": "PERSON_ROUTE_SUPPORTED",
            "linkedin_profile_no_messaging_evidence": "PROFILE_ONLY",
            "general_inbox_ceo_prestige": "CONTACT_HOLD",
            "former_officer_bio_conflict": "CONTACT_HOLD",
            "active_role_without_named_hiring_manager": "CONTACT_HOLD",
            "executive_office_number_vs_company_switchboard": "PERSON_ROUTE_SUPPORTED",
        }
        self.assertEqual({row["name"]: row["expected_bucket"] for row in rows}, expected)
        for row in rows:
            self.assertTrue(row["scenario"])
            self.assertTrue(row["required_findings"])
            self.assertTrue(row["must_not"])
            self.assertNotIn("PASS", row)


if __name__ == "__main__":
    unittest.main()
