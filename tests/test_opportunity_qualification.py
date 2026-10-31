"""Synthetic adversarial tests for opportunity-first qualification."""
import unittest
from datetime import date

from outreach_agent.opportunity_qualification import (
    evaluate_opportunity, audit_opportunity_portfolio,
)


def case(kind="O2B", track="AI_STRATEGY", company="Synthetic Employer"):
    today = date.today().isoformat()
    signal = {"O1": "POSTED_OPENING", "O2A": "PUBLIC_ROLE_CREATION_STATEMENT",
              "O2B": "NONE", "O3": "NONE", "O4": "NONE"}[kind]
    return {
        "schema_version": "1.1",
        "project_id": "PERSONAL_CAREER_OUTREACH",
        "track": track,
        "classification": kind,
        "organization": {"name": company, "parent": company, "work_mode": "TUCSON"},
        "strategic_signal": {
            "claim": "A dated, documented initiative to modernize enterprise operations",
            "source_url": "https://example.org/initiative",
            "published_on": today, "observed_on": today},
        "mandate": {
            "title_or_function": "AI and business transformation executive",
            "employment_signal": signal,
            "evidence_url": "https://example.org/role" if kind in {"O1", "O2A"} else "",
            "employment_hypothesis": kind not in {"O1", "O2A"}},
        "fit": {"resume_basis": "Enterprise AI product strategy and regulated platforms",
                "contribution": "Lead practical enterprise AI transformation",
                "work_arrangement_feasible": True, "credentials_match": True},
        "decision_maker": {
            "name": "Jordan Example", "current_title": "Vice President Technology",
            "role_source_url": "https://example.org/team",
            "initiative_ownership_source_url": "https://example.org/initiative",
            "authority": "DOCUMENTED_INITIATIVE_OWNER",
            "route_type": "MANUAL", "route_url": "https://example.org/team",
            "conversation_thesis": "Explore leadership contribution to a named initiative"},
        "scores": {
            "organization": {"strategic_need": 25, "experience_fit": 22,
                             "leadership_feasibility": 17, "timeliness": 13,
                             "work_mode": 10},
            "person": {"influence": 23, "initiative_ownership": 22,
                       "conversation_value": 18, "route": 12,
                       "role_evidence": 9}},
    }


class OpportunityFirstTests(unittest.TestCase):
    def test_exploration_is_not_hiring(self):
        r = evaluate_opportunity(case())
        self.assertEqual(r["decision"], "EXPLORATORY_REVIEW")
        self.assertEqual(r["hiring_status"], "UNCONFIRMED")
        self.assertFalse(r["contact_ready"])
        self.assertFalse(r["send_authorized"])

    def test_valid_posting_without_named_hiring_manager_is_preserved(self):
        x = case("O1", "PRODUCT_LEADERSHIP")
        x["decision_maker"] = {}
        x["scores"]["person"] = {
            "influence": 0, "initiative_ownership": 0, "conversation_value": 0,
            "route": 0, "role_evidence": 0}
        result = evaluate_opportunity(x)
        self.assertEqual(result["decision"], "ORGANIZATION_REVIEW_EXECUTIVE_PENDING")
        self.assertEqual(result["decision_maker_score"], 0)
        self.assertFalse(result["contact_ready"])
        self.assertFalse(result["send_authorized"])

    def test_emerging_public_mandate_without_executive_is_retained(self):
        x = case("O2A")
        x["decision_maker"] = {}
        x["scores"]["person"] = dict.fromkeys(x["scores"]["person"], 0)
        self.assertEqual(evaluate_opportunity(x)["decision"],
                         "ORGANIZATION_REVIEW_EXECUTIVE_PENDING")

    def test_exploration_without_accountable_executive_remains_hold(self):
        x = case("O2B")
        x["decision_maker"] = {}
        x["scores"]["person"] = dict.fromkeys(x["scores"]["person"], 0)
        self.assertEqual(evaluate_opportunity(x)["decision"], "RESEARCH_HOLD")

    def test_no_executive_cannot_receive_fabricated_person_score(self):
        x = case("O1")
        x["decision_maker"] = {}
        result = evaluate_opportunity(x)
        self.assertEqual(result["decision"], "RESEARCH_HOLD")
        self.assertIn("EXECUTIVE_SCORE_WITHOUT_PERSON_EVIDENCE", result["reasons"])

    def test_portfolio_preserves_real_opportunities_without_people(self):
        x = case("O1")
        x["decision_maker"] = {}
        x["scores"]["person"] = dict.fromkeys(x["scores"]["person"], 0)
        r = audit_opportunity_portfolio([evaluate_opportunity(x)])
        self.assertEqual(r["shortlisted_for_review"], 1)
        self.assertEqual(r["executive_research_pending"], 1)
        self.assertEqual(r["new_contact_ready"], 0)

    def test_posted_product_leader_role(self):
        x = case("O1", "PRODUCT_LEADERSHIP")
        x["mandate"]["title_or_function"] = "Head of Product"
        r = evaluate_opportunity(x)
        self.assertEqual(r["decision"], "SHORTLIST_PENDING_HUMAN_REVIEW")
        self.assertFalse(r["confirmed_new"])

    def test_explicit_role_creation_public_signal(self):
        self.assertEqual(evaluate_opportunity(case("O2A"))["decision"],
                         "SHORTLIST_PENDING_HUMAN_REVIEW")

    def test_ai_initiative_does_not_prove_hiring(self):
        x = case("O2A")
        x["mandate"].update(employment_signal="NONE", evidence_url="")
        r = evaluate_opportunity(x)
        self.assertIn("EMERGING_MANDATE_UNSUPPORTED", r["reasons"])
        self.assertEqual(r["decision"], "RESEARCH_HOLD")

    def test_operator_discussion_requires_authentication(self):
        x = case("O2A")
        x["mandate"].update(employment_signal="OWNER_REPORTED_ROLE_DISCUSSION",
                            evidence_url="")
        self.assertIn("OWNER_ATTESTATION_REQUIRED_PRIVATE_REVIEW",
                      evaluate_opportunity(x)["reasons"])

    def test_ceo_prestige_not_equal_sponsorship(self):
        x = case()
        x["decision_maker"]["current_title"] = "Chief Executive Officer"
        x["decision_maker"]["authority"] = "UNVERIFIED"
        x["scores"]["person"] = {"influence": 30, "initiative_ownership": 25,
                                 "conversation_value": 20, "route": 15,
                                 "role_evidence": 10}
        self.assertIn("EXECUTIVE_SPONSOR_NOT_ESTABLISHED",
                      evaluate_opportunity(x)["reasons"])

    def test_missing_individual_route_holds_even_with_high_score(self):
        x = case()
        x["decision_maker"].update(route_type="NO_ROUTE", route_url="")
        self.assertIn("NO_PERSON_SPECIFIC_ROUTE", evaluate_opportunity(x)["reasons"])

    def test_generic_contact_form_cannot_pass_as_person_route(self):
        x = case()
        x["decision_maker"].update(route_type="INDIRECT",
                                   route_url="https://example.org/contact")
        self.assertIn("INDIRECT_ROUTE_REQUIRES_PERSON_SPECIFIC_REVIEW",
                      evaluate_opportunity(x)["reasons"])

    def test_unfeasible_qualification_or_employment_holds(self):
        for key, reason in [
            ("credentials_match", "REQUIRED_CREDENTIALS_NOT_MATCHED"),
            ("work_arrangement_feasible", "WORK_ARRANGEMENT_NOT_VERIFIED_FEASIBLE"),
        ]:
            with self.subTest(key=key):
                x = case()
                x["fit"][key] = False
                self.assertIn(reason, evaluate_opportunity(x)["reasons"])

    def test_undated_organization_signal_holds(self):
        x = case()
        x["strategic_signal"]["published_on"] = None
        self.assertIn("STRATEGIC_SOURCE_FRESHNESS_UNVERIFIED",
                      evaluate_opportunity(x)["reasons"])

    def test_unsubstantiated_ownership_holds(self):
        x = case()
        x["decision_maker"]["initiative_ownership_source_url"] = ""
        self.assertIn("ACCOUNTABLE_EXECUTIVE_NOT_CORROBORATED",
                      evaluate_opportunity(x)["reasons"])

    def test_perfect_score_cannot_override_missing_role_evidence(self):
        x = case("O1")
        x["mandate"]["evidence_url"] = ""
        x["scores"]["organization"] = {
            "strategic_need": 30, "experience_fit": 25, "leadership_feasibility": 20,
            "timeliness": 15, "work_mode": 10}
        x["scores"]["person"] = {
            "influence": 30, "initiative_ownership": 25, "conversation_value": 20,
            "route": 15, "role_evidence": 10}
        self.assertEqual(evaluate_opportunity(x)["decision"], "RESEARCH_HOLD")

    def test_score_cap_and_unexpected_private_field_rejected(self):
        x = case()
        x["scores"]["person"]["influence"] = 31
        with self.assertRaisesRegex(ValueError, "Score outside cap"):
            evaluate_opportunity(x)
        x = case()
        x["private_email"] = "secret@example.org"
        with self.assertRaisesRegex(ValueError, "Unexpected"):
            evaluate_opportunity(x)

    def test_cross_project_record_holds(self):
        x = case()
        x["project_id"] = "NOVA_SUBCONTRACTING"
        r = evaluate_opportunity(x)
        self.assertIn("PROJECT_ID_NOT_VERIFIED", r["reasons"])

    def test_o3_o4_general_relevance_not_shortlisted(self):
        for kind in ("O3", "O4"):
            self.assertEqual(evaluate_opportunity(case(kind))["decision"], "RESEARCH_HOLD")

    def test_portfolio_three_two_with_distinct_organizations(self):
        rows = [
            evaluate_opportunity(case(track=t, company="Employer " + str(i)))
            for i, t in enumerate(["AI_STRATEGY"] * 3 + ["PRODUCT_LEADERSHIP"] * 2)
        ]
        r = audit_opportunity_portfolio(rows)
        self.assertEqual(r["shortlisted_for_review"], 5)
        self.assertEqual(r["portfolio_warnings"], [])
        self.assertEqual(r["new_contact_ready"], 0)

    def test_portfolio_flags_concentration_and_wrong_mix(self):
        rows = [evaluate_opportunity(case(company="Employer Parent")) for _ in range(5)]
        warnings = audit_opportunity_portfolio(rows)["portfolio_warnings"]
        self.assertIn("DUPLICATE_ORGANIZATION", warnings)
        self.assertIn("PILOT_PARENT_ORGANIZATION_CONCENTRATION", warnings)
        self.assertIn("PILOT_ALLOCATION_DEVIATION", warnings)

    def test_portfolio_reports_shortfall_not_weak_backfill(self):
        rows = [evaluate_opportunity(case()), evaluate_opportunity(case("O3"))]
        r = audit_opportunity_portfolio(rows)
        self.assertEqual((r["shortlisted_for_review"], r["shortfall"]), (1, 4))

    def test_legacy_export_does_not_accept_opportunity_fields(self):
        from outreach_agent.drive_review_packet import build_review_packet
        payload = {"project_id": "PERSONAL_CAREER_OUTREACH",
                   "run_id": "research-001",
                   "date_local": date.today().isoformat(),
                   "candidates": [], "opportunities": []}
        with self.assertRaisesRegex(ValueError, "exact"):
            build_review_packet(payload)


if __name__ == "__main__":
    unittest.main()
