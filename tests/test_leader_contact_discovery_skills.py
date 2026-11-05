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

    def test_ten_adversarial_examples_cover_expected_buckets_without_fake_passes(self):
        self.assertEqual(self.cases["assurance"], "UNEXECUTED_TEST_SCENARIOS")
        rows = self.cases["cases"]
        self.assertEqual(len(rows), 10)
        self.assertEqual(len({row["name"] for row in rows}), len(rows))
        expected = {
            "official_named_work_email": "PERSON_ROUTE_SUPPORTED",
            "linkedin_profile_no_messaging_evidence": "PROFILE_ONLY",
            "general_inbox_ceo_prestige": "CONTACT_HOLD",
            "former_officer_bio_conflict": "CONTACT_HOLD",
            "active_role_without_named_hiring_manager": "CONTACT_HOLD",
            "executive_office_number_vs_company_switchboard": "PERSON_ROUTE_SUPPORTED",
            "already_researched_high_profile_executive": "PERSON_ROUTE_SUPPORTED",
            "new_initiative_at_known_employer": "PROFILE_ONLY",
            "weak_two_employer_search_breadth": "PROFILE_ONLY",
            "existing_ai_chief_no_distinct_role": "PROFILE_ONLY",
        }
        self.assertEqual({row["name"]: row["expected_bucket"] for row in rows}, expected)
        for row in rows:
            self.assertTrue(row["scenario"])
            self.assertTrue(row["required_findings"])
            self.assertTrue(row["must_not"])
            self.assertNotIn("PASS", row)


    def test_focused_depth_and_promising_prospects(self):
        orch = self.skill["daily-executive-outreach"]
        brief_skill = self.skill["daily-executive-brief"]
        contact = self.skill["contact-verification"]
        org = (SKILL_ROOT / "organization-discovery" / "SKILL.md").read_text(encoding="utf-8")
        for content in (orch, org, self.brief):
            self.assertIn("5–8", content)
        for content in (orch, org, self.brief):
            self.assertIn("best three", " ".join(content.split()))
        self.assertIn("PROMISING_RESEARCH_PROSPECTS", brief_skill)
        self.assertIn("PROMISING_RESEARCH_PROSPECTS", self.brief)
        self.assertIn("Do not stop just because an individual profile", contact)
        self.assertIn("professional-conversation relevance", self.brief)
        self.assertIn("SEND_AUTHORIZED", self.brief)



    def test_prior_research_baseline_is_public_only_and_prevents_repeat_claims(self):
        baseline = json.loads(
            (ROOT / "config" / "public-career-research-baseline.json").read_text(encoding="utf-8")
        )
        self.assertEqual(baseline["scope"], "PUBLIC_RESEARCH_ONLY")
        self.assertIn("TMC Health", baseline["previously_screened_employers"])
        self.assertIn("Tucson Electric Power", baseline["previously_screened_employers"])
        known = {(p["name"], p["employer"]) for p in baseline["previously_researched_people"]}
        self.assertIn(("Josh Lee", "TMC Health"), known)
        self.assertIn(("Susan Gray", "Tucson Electric Power"), known)
        self.assertIn(("Dallas Dukes", "Tucson Electric Power"), known)
        self.assertEqual(len(known), len(baseline["previously_researched_people"]))
        self.assertTrue(all(set(p) == {"name", "employer"} for p in baseline["previously_researched_people"]))
        for forbidden in ("previously_met", "private_email", "personal_phone",
                          "relationship_status", "sent_at", "@"):
            self.assertNotIn(forbidden, json.dumps(baseline).lower())
        for skill in ("daily-executive-outreach", "organization-discovery",
                      "run-quality-audit", "daily-executive-brief"):
            self.assertIn("public-career-research-baseline.json", self.skill[skill]
                          if skill in self.skill else
                          (SKILL_ROOT / skill / "SKILL.md").read_text(encoding="utf-8"))

    def test_leader_ranking_requires_business_proximity_not_ceo_prestige(self):
        leadership = self.skill["leadership-discovery"]
        qualification = (SKILL_ROOT / "relationship-qualification" / "SKILL.md").read_text(encoding="utf-8")
        for phrase in ("Decision-maker selection", "outcome owner",
                       "primary", "CEO", "FUNCTIONALLY_PLAUSIBLE"):
            self.assertIn(phrase.lower(), leadership.lower())
        for phrase in ("affected users/workflow", "bounded", "CONTRIBUTION_UNCLEAR"):
            self.assertIn(phrase, qualification)
        self.assertIn("Why this person", qualification)

    def test_contact_research_checks_three_lanes_and_historical_purpose(self):
        contact = self.skill["contact-verification"]
        for phrase in ("at least three distinct public-source lanes",
                       "government/utility", "contract PDFs",
                       "HISTORICAL_PERSON_WORK_CONTACT_RECHECK",
                       "PURPOSE_RESTRICTED_ROUTE_REVIEW",
                       "CURRENT_PERSON_WORK_ROUTE"):
            self.assertIn(phrase, contact)
            self.assertIn(phrase.split("_")[0] if "_" in phrase else phrase,
                          contact)
        for phrase in ("HISTORICAL_PERSON_WORK_CONTACT_RECHECK",
                       "PURPOSE_RESTRICTED_ROUTE_REVIEW",
                       "PROMISING_RESEARCH_PROSPECTS"):
            self.assertIn(phrase, self.brief)
        self.assertIn("person-contact binding", self.skill["run-quality-audit"])
        self.assertIn("published professional route", self.skill["daily-executive-brief"])



    def test_local_initiative_must_be_supported_separately_from_local_site(self):
        org = (SKILL_ROOT / "organization-discovery" / "SKILL.md").read_text(encoding="utf-8")
        orchestrator = self.skill["daily-executive-outreach"]
        audit = self.skill["run-quality-audit"]
        brief = self.skill["daily-executive-brief"]
        for required in ("LOCAL_SITE_CONFIRMED", "LOCAL_INITIATIVE_CONFIRMED",
                         "LOCAL_INITIATIVE_UNVERIFIED", "Tempe/Phoenix",
                         "REMOTE_US_FEASIBILITY_UNVERIFIED"):
            self.assertIn(required, org)
        self.assertIn("LOCAL_INITIATIVE_UNVERIFIED", audit)
        self.assertIn("LOCAL_INITIATIVE_UNVERIFIED", brief)
        self.assertIn("Tucson-area initiative", orchestrator)
        self.assertIn("Tempe expansion plus a Tucson office", self.brief)

    def test_sponsor_and_first_conversation_target_are_separate(self):
        leadership = self.skill["leadership-discovery"]
        brief = self.skill["daily-executive-brief"]
        audit = self.skill["run-quality-audit"]
        for required in ("ACCOUNTABLE_SPONSOR", "FIRST_CONVERSATION_TARGET",
                         "FIRST_CONVERSATION_TARGET_CANDIDATE",
                         "RESEARCH_HOLD", "DOCUMENTED"):
            self.assertIn(required, leadership)
        self.assertIn("source-verified operating VP", self.brief)
        self.assertIn("ACCOUNTABLE_SPONSOR", brief)
        self.assertIn("practical first-conversation candidate", audit)
        self.assertIn("historical VP title", audit)

    def test_bounded_contact_stop_and_distinct_contribution(self):
        contact = self.skill["contact-verification"]
        orchestrator = self.skill["daily-executive-outreach"]
        qualification = (SKILL_ROOT / "relationship-qualification" / "SKILL.md").read_text(encoding="utf-8")
        for required in ("one pass per lane", "one targeted source recheck",
                         "CONTACT_SEARCH_COMPLETED_NO_SUITABLE_ROUTE",
                         "next already-screened qualified employer"):
            self.assertIn(required, contact.replace("**", ""))
        self.assertIn("three-lane contact search", orchestrator)
        self.assertIn("CONTRIBUTION_UNCLEAR", qualification)
        self.assertIn("one initiative-specific decision", qualification)
        self.assertIn("incumbent owner", qualification)
        self.assertIn("CONTACT_SEARCH_COMPLETED_NO_SUITABLE_ROUTE", self.brief)
        self.assertIn("CONTRIBUTION_UNCLEAR", self.brief)
        self.assertIn("CONTACT_READY=false", self.skill["daily-executive-brief"])


    def test_public_research_index_reconciles_all_four_discovery_rounds(self):
        baseline = json.loads(
            (ROOT / "config" / "public-career-research-baseline.json").read_text(encoding="utf-8")
        )
        employers = set(baseline["previously_screened_employers"])
        people = {(p["name"], p["employer"]) for p in baseline["previously_researched_people"]}
        self.assertGreaterEqual(len(employers), 45)
        self.assertGreaterEqual(len(people), 32)
        for employer in ("Tucson Airport Authority", "ARTO",
                         "Critical Path Institute", "Pima County",
                         "Freeport-McMoRan", "Honeywell Aerospace",
                         "GitLab", "Red Robin", "Veralto"):
            self.assertIn(employer, employers)
        for key in (("Anthony Casella", "Tucson Airport Authority"),
                    ("Armen Alajian", "ARTO"),
                    ("Michelle Simon", "Pima County"),
                    ("Ramona Walls", "Critical Path Institute"),
                    ("Cory Stevens", "Freeport-McMoRan")):
            self.assertIn(key, people)
        self.assertEqual(len(employers), len(baseline["previously_screened_employers"]))
        self.assertEqual(len(people), len(baseline["previously_researched_people"]))
        self.assertIn("private", json.dumps(baseline["limitations"]).lower())
        self.assertNotIn("@", json.dumps(baseline))
        self.assertTrue(all(set(row) == {"name", "employer"} for row in baseline["previously_researched_people"]))

    def test_arto_shared_inbox_and_media_email_are_not_direct_routes(self):
        contact = self.skill["contact-verification"]
        brief_skill = self.skill["daily-executive-brief"]
        audit = self.skill["run-quality-audit"]
        for fragment in ("SHARED_INBOX_CONTEXTUAL_INVITATION",
                         "PURPOSE_RESTRICTED_ROUTE_REVIEW",
                         "howdy@", "PERSON_ROUTE_SUPPORTED"):
            self.assertIn(fragment, contact)
            self.assertIn(fragment, self.brief)
        self.assertIn("SHARED_INBOX_CONTEXTUAL_INVITATION", brief_skill)
        self.assertIn("SHARED_INBOX_CONTEXTUAL_INVITATION", audit)
        self.assertIn("armen@", audit)
        self.assertIn("not a direct named email", audit)
        self.assertIn("A contact route never equals consent", self.brief)

    def test_career_fit_distinct_from_contact_accessibility(self):
        qualification = (SKILL_ROOT / "relationship-qualification" / "SKILL.md").read_text(encoding="utf-8")
        org = (SKILL_ROOT / "organization-discovery" / "SKILL.md").read_text(encoding="utf-8")
        leader = self.skill["leadership-discovery"]
        for label in ("CONVERSATION_WORTH_EXPLORING", "PROMISING_RESEARCH_ONLY", "LOW_CAREER_FIT"):
            self.assertIn(label, qualification)
            self.assertIn(label, self.brief)
            self.assertIn(label, self.skill["daily-executive-brief"])
        self.assertIn("production staff", org)
        self.assertIn("LOW_CAREER_FIT", leader)
        self.assertIn("contact route cannot improve", qualification)
        self.assertIn("Never rank a weak-fit owner", self.brief)



if __name__ == "__main__":
    unittest.main()
