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
        self.assertIn("required recent AI-led workflow transformation with changed workflows and measured outcomes", " ".join(risepoint["explanation_must_include"]))
        uofa = cases["university_of_arizona_role_and_initiative_comparison"]["expected"]
        self.assertIn("Chief AI and Data Science Officer / ORAI leadership", uofa["must_keep_org_structure"])
        self.assertTrue(cases["missing_route_does_not_lower_opportunity_quality"]["expected"]["opportunity_order_changes_due_to_route"] is False)
        self.assertFalse(cases["research_only_never_contact_ready"]["expected"]["contact_ready"])

    def test_ranked_opportunity_table_header_and_separator_column_counts_match(self):
        template = (ROOT / "references" / "daily-brief-template.md").read_text(encoding="utf-8")
        lines = template.splitlines()
        header_index = next(
            index for index, line in enumerate(lines)
            if line.startswith("| Category / rank |")
        )
        header = lines[header_index]
        separator = lines[header_index + 1]

        header_columns = len(header.strip().strip("|").split("|"))
        separator_columns = len(separator.strip().strip("|").split("|"))
        self.assertEqual(header_columns, 12)
        self.assertEqual(separator_columns, header_columns)

    def test_candidate_fit_categories_separate_quality_feasibility_and_contact_readiness(self):
        method = (ROOT / "references" / "opportunity-assessment.md").read_text(encoding="utf-8")
        template = (ROOT / "references" / "daily-brief-template.md").read_text(encoding="utf-8")
        profile = (ROOT / "config" / "public-candidate-profile.md").read_text(encoding="utf-8")

        for category in ("RECOMMENDED", "CONDITIONAL", "WATCHLIST"):
            self.assertIn(category, method)
            self.assertIn(category, template)
        self.assertIn("NOT_EVIDENCED", method)
        self.assertIn("not proof", method)
        self.assertIn("NOT_MET", method)
        self.assertIn("confirmed incompatible location", method)
        self.assertIn("No CONDITIONAL or WATCHLIST opportunity can outrank a genuinely RECOMMENDED opportunity", method)
        self.assertIn("contact readiness", method.lower())
        self.assertIn("Phoenix hybrid", method)
        self.assertIn("relocation is not acceptable", method.lower())
        self.assertIn("Priority 1", profile)
        self.assertIn("Priority 2", profile)
        self.assertIn("Priority 3", profile)
        self.assertIn("Relocation", profile)
        for timeline_item in (
            "September 2018–July 2020",
            "July 2020–December 2023",
            "January 2024–present",
            "approximately 8 years and 2 months",
        ):
            self.assertIn(timeline_item, profile)
        self.assertIn("matrix product-team leadership", profile)
        self.assertIn("direct-report status", profile)
        self.assertIn("without exclusive ownership of formal reviews", profile)

        self.assertIn("Owner-verification record", method)
        self.assertIn("NOT_PROVIDED", template)
        for field in (
            "Product-management and senior-leadership tenure",
            "Direct people management",
            "AI product or transformation delivery",
            "Budget, portfolio, program, and organizational scope",
            "Industry-specific experience and transferability",
            "Eligibility and role-level preferences",
        ):
            self.assertIn(field, template)
        self.assertIn("Never commit a private resume or relationship history", method)

    def test_candidate_fit_acceptance_scenarios_enforce_location_and_evidence_rules(self):
        data = json.loads((ROOT / "evals" / "opportunity_first_acceptance.json").read_text(encoding="utf-8"))
        cases = {case["id"]: case for case in data["cases"]}
        required = {
            "location_infeasible_high_need_cannot_outrank_feasible_recommendation",
            "phoenix_hybrid_requires_schedule_confirmation",
            "missing_mandatory_evidence_is_conditional_not_not_met",
            "verified_mandatory_mismatch_is_watchlist_below_recommended",
            "confirmed_location_preferences_control_eligibility",
        }
        self.assertTrue(required.issubset(cases))

        location = cases["location_infeasible_high_need_cannot_outrank_feasible_recommendation"]["expected"]
        opportunities = cases["location_infeasible_high_need_cannot_outrank_feasible_recommendation"]["opportunities"]
        self.assertEqual(location["category_order"], ["RECOMMENDED", "CONDITIONAL", "WATCHLIST"])
        self.assertEqual(location["candidate_recommendation_order"][0], "Tucson enterprise product director")
        self.assertEqual([item["category"] for item in opportunities],
                         ["RECOMMENDED", "WATCHLIST", "WATCHLIST"])
        self.assertTrue(location["must_preserve_organizational_quality_for_watchlist"])

        unknown = cases["missing_mandatory_evidence_is_conditional_not_not_met"]
        self.assertEqual(unknown["opportunities"][0]["mandatory_requirement_status"], "NOT_EVIDENCED")
        self.assertEqual(unknown["opportunities"][0]["category"], "CONDITIONAL")
        mismatch = cases["verified_mandatory_mismatch_is_watchlist_below_recommended"]
        self.assertEqual([item["category"] for item in mismatch["opportunities"]],
                         ["RECOMMENDED", "WATCHLIST"])

        preferences = cases["confirmed_location_preferences_control_eligibility"]["expected"]["preferences"]
        self.assertEqual(preferences["phoenix_hybrid"], "CONDITIONAL_UNTIL_SCHEDULE_AND_COMMUTE_CONFIRMED")
        self.assertEqual(preferences["relocation"], "NOT_ACCEPTABLE")

    def test_owner_reported_profile_facts_and_candidate_fit_calibration(self):
        profile = (ROOT / "config" / "public-candidate-profile.md").read_text(encoding="utf-8")
        data = json.loads((ROOT / "evals" / "opportunity_first_acceptance.json").read_text(encoding="utf-8"))
        self.assertIn("Owner-reported career scope (owner-confirmed; not independently verified)", profile)
        self.assertIn("Approximately 12 cumulative years", profile)
        self.assertIn("four direct-report Product Managers", profile)
        self.assertIn("Three Business Analysts report through", profile)
        self.assertIn("not direct reports", profile)
        self.assertIn("formal CPO title", profile)
        self.assertIn("Tucson / Southern Arizona", profile)
        self.assertIn("Relocation", profile)

        cases = {case["id"]: case for case in data["cases"]}
        ua = cases["university_of_arizona_role_and_initiative_comparison"]
        ua_text = " ".join(ua["expected"]["must_state"])
        self.assertIn("supports the posting's five-year managerial minimum", ua_text)
        self.assertNotIn("five years of managerial experience is not established", ua_text)
        risepoint = cases["risepoint_product_role_vs_architecture_role"]
        rp_text = " ".join(risepoint["expected"]["explanation_must_include"])
        self.assertIn("Commercial AI product delivery is now OWNER_REPORTED", rp_text)
        self.assertIn("measured outcomes", rp_text)
        self.assertIn("large-scale engineering-organization ownership", rp_text)

        calibration = cases["owner_reported_management_and_commercial_ai_evidence_calibration"]["expected"]
        self.assertIn("quantified AI performance improvements", calibration["still_not_evidenced"])
        self.assertIn("sole final budget approval or direct P&L ownership", calibration["still_not_evidenced"])
        self.assertIn("quantified AI performance improvements", calibration["still_not_evidenced"][0])
        self.assertIn("exclusive ownership", calibration["still_not_evidenced"][-1])
        self.assertIn("Candidate fit does not imply contact readiness", calibration["governance"])
        self.assertEqual(calibration["location"], "Preserve the existing Tucson/Southern Arizona, fully remote U.S., conditional Phoenix hybrid, no relocation rules.")

        phase32 = cases["phase_3_2_product_tenure_and_matrix_leadership_reconciliation"]
        self.assertIn("8 years and 2 months", phase32["calendar_product_role_tenure_as_of_2026_11"])
        phase32_expected = phase32["expected"]
        self.assertIn("SUPPORTED", phase32_expected["risepoint_8_year_product_requirement"])
        self.assertIn("NOT_EVIDENCED", phase32_expected["risepoint_8_year_product_requirement"])
        self.assertIn("SUPPORTED", phase32_expected["university_of_arizona_5_year_management_requirement"])
        self.assertIn("matrix", phase32_expected["three_year_group_product_leadership_requirement"])
        self.assertIn("direct reports", " ".join(phase32_expected["must_not"]))
        self.assertIn("exclusive ownership", " ".join(phase32_expected["must_not"]))

    def test_candidate_tenure_and_leadership_types_are_not_conflated_in_fixtures(self):
        data = json.loads((ROOT / "evals" / "opportunity_first_acceptance.json").read_text(encoding="utf-8"))
        cases = {case["id"]: case for case in data["cases"]}
        risepoint = cases["risepoint_product_role_vs_architecture_role"]
        resume_evidence = " ".join(risepoint["candidate_evidence"])
        self.assertIn("September 2018", resume_evidence)
        self.assertIn("approximately 8 years and 2 months", resume_evidence)
        ua = cases["university_of_arizona_role_and_initiative_comparison"]
        self.assertIn("supports the posting's five-year managerial minimum", " ".join(ua["expected"]["must_state"]))
        self.assertIn("not counted as direct management", " ".join(ua["expected"]["must_state"]))
        prior = cases["reassessment_prior_opportunities_after_owner_evidence_2026_11_10"]
        paylocity = next(item for item in prior["opportunities"] if item["organization"] == "Paylocity")
        self.assertIn("8 years and 2 months", paylocity["candidate_match"])
        self.assertIn("NOT_EVIDENCED", paylocity["candidate_match"])

    def test_amgen_roles_are_compared_by_actual_requirements(self):
        data = json.loads((ROOT / "evals" / "opportunity_first_acceptance.json").read_text(encoding="utf-8"))
        case = next(case for case in data["cases"] if case["id"] == "amgen_role_requirement_by_requirement_calibration")
        self.assertEqual(len(case["opportunities"]), 3)
        expected = case["expected"]
        self.assertIn("four-year leadership threshold is supported", expected["director"])
        self.assertIn("NOT_EVIDENCED", expected["product_operations"])
        self.assertTrue(any("preferred qualifications" in item for item in expected["must_not"]))


    def test_fresh_discovery_rank_uses_owner_evidence_without_inflating_fit(self):
        data = json.loads((ROOT / "evals" / "opportunity_first_acceptance.json").read_text(encoding="utf-8"))
        case = next(case for case in data["cases"] if case["id"] == "reassessment_prior_opportunities_after_owner_evidence_2026_11_10")
        self.assertEqual(case["sample_type"], "REASSESSMENT_OF_PREVIOUSLY_IDENTIFIED_OPPORTUNITIES_NOT_AN_INDEPENDENT_FRESH_EMPLOYER_SAMPLE")
        opportunities = case["opportunities"]
        self.assertEqual([item["organization"] for item in opportunities], [
            "NielsenIQ", "Paylocity", "UnitedHealth Group / Optum Tech", "Tucson Electric Power"
        ])
        self.assertEqual(opportunities[0]["category"], "RECOMMENDED")
        self.assertTrue(all(item["category"] == "CONDITIONAL" for item in opportunities[1:]))
        self.assertIn("NOT_EVIDENCED", opportunities[1]["candidate_match"])
        self.assertIn("large-scale enterprise transformation", opportunities[2]["candidate_match"])
        self.assertIn("Electric-utility capital plans/systems/regulatory experience are NOT_EVIDENCED", opportunities[3]["candidate_match"])
        self.assertIn("12 management years as 12 years product management", " ".join(case["comparison"]["must_not"]))
        self.assertIn("contact readiness", " ".join(case["comparison"]["must_not"]))

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

