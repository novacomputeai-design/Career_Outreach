"""Static contract checks for opportunity-first discovery.

These checks protect the research order, separation of opportunity and person
qualification, and the content of manual Codex acceptance fixtures. They do
not execute Codex, validate live sources, or prove native skill activation.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"


def read_skill(name):
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")


class OpportunityFirstContractTests(unittest.TestCase):
    def test_shared_method_ranks_opportunities_before_people(self):
        method = (ROOT / "references" / "opportunity-assessment.md").read_text(encoding="utf-8")
        self.assertIn("Compare and rank before people research", method)
        self.assertIn("DIRECT_HIRING", method)
        self.assertIn("STRATEGIC_EXPLORATION", method)
        self.assertIn("whether a person-specific public route exists", method)
        self.assertIn("A strong research opportunity remains reportable", method)

        discovery = read_skill("organization-discovery")
        self.assertLess(discovery.index("capture the opportunity record and provisional ranking before researching people"),
                        discovery.index("Rank and compare opportunities provisionally before triggering person research"))

    def test_person_score_and_contact_gates_do_not_change_opportunity_rank(self):
        qualification = read_skill("relationship-qualification")
        self.assertIn("must not determine or alter opportunity rank", qualification)
        self.assertIn("does not lower organizational opportunity quality", qualification)
        rubric = (ROOT / "references" / "scoring-rubric.md").read_text(encoding="utf-8")
        self.assertIn("person-to-person career connection only", rubric)
        self.assertIn("missing route", rubric)

    def test_mandatory_qualifications_and_leadership_evidence_have_distinct_rank_rules(self):
        method = (ROOT / "references" / "opportunity-assessment.md").read_text(encoding="utf-8")
        self.assertIn("candidate feasibility", method)
        self.assertIn("mandatory qualifications or eligibility are unmet or unverified", method)
        self.assertIn("Mere accessibility", method)
        self.assertIn("Record the prior rank, new fact and source", method)
        leadership = read_skill("leadership-discovery")
        self.assertIn("Leadership research can reveal material facts about organizational needs", leadership)
        self.assertIn("Contact accessibility, route availability", leadership)

    def test_discovery_coverage_and_strategic_evidence_floor_are_explicit(self):
        method = (ROOT / "references" / "opportunity-assessment.md").read_text(encoding="utf-8")
        for phrase in (
            "Discovery coverage and evidence floor",
            "TUCSON_SOUTHERN_AZ",
            "US_REMOTE",
            "current direct-hiring leadership roles",
            "current organizational need signals",
            "plausible, bounded leadership contribution",
            "meaningful organizational need",
            "CONTEXT_ONLY",
            "material rejects",
            "organizational opportunity quality",
            "candidate feasibility",
            "contact readiness",
        ):
            self.assertIn(phrase, method)
        discovery = read_skill("organization-discovery")
        self.assertIn("including zero-results", discovery)
        self.assertIn("material rejected alternatives", discovery)
        self.assertIn("general announcements stay context until validated", discovery)

    def test_coverage_ledger_records_observed_research_and_marks_unknowns(self):
        template = (ROOT / "references" / "daily-brief-template.md").read_text(encoding="utf-8")
        for field in (
            "Actual query or target",
            "Source checked",
            "Date checked / source date",
            "Result count",
            "Research outcome, including failure or access limit",
            "NOT_RECORDED",
        ):
            self.assertIn(field, template)
        self.assertNotIn("seven-employer supervised discovery", template)
        example = (ROOT / "evals" / "phase2_coverage_ledger_example.md").read_text(encoding="utf-8")
        for employer in (
            "Pima County", "RTX", "Banner Health", "Mister Car Wash",
            "Amgen", "Johnson & Johnson", "UnitedHealth Group",
        ):
            self.assertIn(employer, example)
        self.assertIn("returned 404", example)
        self.assertIn("not accessible/retained", example)
        self.assertIn("Exact search strings and result counts were not retained", example)
        self.assertIn("NOT_RECORDED", example)

    def test_strategic_exploration_does_not_infer_vacancy_or_invitation(self):
        method = (ROOT / "references" / "opportunity-assessment.md").read_text(encoding="utf-8")
        template = (ROOT / "references" / "daily-brief-template.md").read_text(encoding="utf-8")
        for text in (method, template):
            self.assertIn("meaningful organizational need", text)
            self.assertIn("plausible, bounded", text)
            self.assertIn("willingness to meet", text)
            self.assertIn("invitation", text)
        self.assertIn("does not establish an advertised or unadvertised vacancy", method)
        self.assertIn("does not imply a vacancy", template)

    def test_daily_brief_reports_opportunities_before_people(self):
        template = (ROOT / "references" / "daily-brief-template.md").read_text(encoding="utf-8")
        self.assertLess(template.index("## Ranked career opportunities"),
                        template.index("## Relevant people and professional routes"))
        self.assertLess(template.index("## Relevant people and professional routes"),
                        template.index("## Contact-ready people"))
        self.assertIn("Opportunity totals never count toward the person target", template)
        self.assertIn("## Research coverage ledger", template)
        self.assertIn("zero-result passes", template)
        self.assertIn("rejected/held leads", template)

    def test_acceptance_scenarios_cover_requested_cases(self):
        data = json.loads((ROOT / "evals" / "opportunity_first_acceptance.json").read_text(encoding="utf-8"))
        self.assertEqual(data["assurance"], "MANUAL_CODEX_RUN_REQUIRED")
        cases = {case["id"]: case for case in data["cases"]}
        required = {
            "risepoint_product_role_vs_architecture_role",
            "university_of_arizona_role_and_initiative_comparison",
            "strategic_opportunity_without_vacancy",
            "missing_route_does_not_lower_opportunity_quality",
            "research_only_never_contact_ready",
            "mandatory_qualification_affects_candidate_feasibility",
            "leadership_evidence_can_revise_rank_contact_access_cannot",
        }
        self.assertTrue(required.issubset(cases))
        risepoint = cases["risepoint_product_role_vs_architecture_role"]["expected"]
        self.assertEqual(risepoint["relative_ranking"], ["JR101253", "JR101288"])
        self.assertIn("mandatory recent AI-led workflow transformation outcomes", " ".join(risepoint["explanation_must_include"]))
        uofa = cases["university_of_arizona_role_and_initiative_comparison"]["expected"]
        self.assertIn("Chief AI and Data Science Officer / ORAI leadership", uofa["must_keep_org_structure"])
        self.assertTrue(cases["missing_route_does_not_lower_opportunity_quality"]["expected"]["opportunity_order_changes_due_to_route"] is False)
        self.assertFalse(cases["research_only_never_contact_ready"]["expected"]["contact_ready"])

    def test_governance_and_codex_activation_boundaries_remain(self):
        policy = json.loads((ROOT / "config" / "operating-policy.json").read_text(encoding="utf-8"))
        self.assertFalse(policy["outreach"]["automatic_sending"])
        self.assertTrue(policy["outreach"]["individual_draft_approval"])
        self.assertTrue(policy["outreach"]["separate_send_authorization"])
        self.assertEqual(policy["governance"]["history_unavailable"], "HOLD_UNVERIFIED")

        orchestrator = read_skill("daily-executive-outreach")
        self.assertIn("report NOT_VERIFIED", orchestrator)
        self.assertIn("lack of private history means novelty UNVERIFIED", orchestrator)
        self.assertIn("Keep the target of up to 20 new verified people separate from opportunity counts", orchestrator)


if __name__ == "__main__":
    unittest.main()

