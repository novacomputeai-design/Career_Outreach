"""V2.1 integration preflight tests against the actual repository assessor.

No web, DPAPI, messages, applications, external data or send capabilities.
"""
import copy
import unittest
from datetime import date, timedelta
from outreach_agent.career_intelligence import (
    evaluate_opportunity, assess_owner_feedback, opportunity_identity, audit_packet,
)

TODAY = date.today().isoformat()

def claim(cid, kind, text, *, subject="org-1", obj=None, url="https://employer.example/strategy"):
    return {"claim_id": cid, "claim_type": kind, "claim_text": text,
            "source_url": url, "publisher": "Example Employer",
            "source_origin_id": "employer-original", "retrieved_at": TODAY,
            "published_on": TODAY, "page_read_success": True,
            "excerpt": "The company confirms: " + text,
            "support_relationship": "DIRECT", "subject_id": subject,
            "object_id": obj}

def sample(pathway="STRATEGIC_EXPLORATION", executive=False):
    c = claim("objective", "BUSINESS_OBJECTIVE",
              "Modernize enterprise platforms and evaluate responsible AI.")
    r = {"schema_version": "2.1", "project_id": "PERSONAL_CAREER_OUTREACH",
         "purpose": "Explore personal senior leadership career opportunities",
         "engagement_pathway": pathway, "capability_theme": "BOTH",
         "organization": {"organization_id": "org-1", "name": "Example Employer",
                          "work_mode": "TUCSON", "feasible": True},
         "initiative": {"initiative_id": "initiative-1", "objective_claim_id": "objective"},
         "claims": [c],
         "contribution": {
             "business_objective_claim_id": "objective",
             "candidate_basis": "Enterprise product strategy and AI prioritization experience",
             "candidate_claim_approved": True,
             "proposed_value": "Explore portfolio leadership for responsible enterprise AI adoption",
             "mandate_key": "enterprise-ai-product", "leadership_need_assumed": False,
             "hiring_claim": False},
         "executive": None, "job": None}
    if pathway == "DIRECT_HIRING":
        r["job"] = {"requisition_id": "req-123", "official_ats_url": "https://employer.example/jobs/req-123",
                    "status_claim_id": "job-current", "state": "ACCEPTING",
                    "mandatory_qualifications": [
                        {"requirement": "Relevant experience", "status": "MATCHED",
                         "candidate_evidence_refs": ["candidate-profile:experience"]}],
                    "work_mode_feasible": True,
                    "candidate_eligibility": {"work_authorization": "ELIGIBLE"},
                    "role_relevance": "MATCH"}
        r["claims"].append(claim("job-current", "JOB_ACTIVE",
                    "Applications are open for req-123.", obj="req-123",
                    url="https://employer.example/jobs/req-123"))
    if executive:
        r["executive"] = {
            "person_id": "person-a", "name": "Pat Example",
            "current_role_claim_id": "current-role", "opted_out": False,
            "ownership": {"role_type": "BUSINESS_OUTCOME_OWNER",
                          "ownership_grade": "DOCUMENTED", "claim_id": "ownership"},
            "route": {"route_type": "WARM_INTRO",
                      "url": "https://association.example/introductions",
                      "verified_for_person": True}}
        r["claims"].extend([
            claim("current-role", "CURRENT_EXECUTIVE_ROLE",
                  "Pat Example serves as business vice president.", subject="person-a", obj="org-1"),
            claim("ownership", "EXECUTIVE_OWNERSHIP",
                  "Pat Example sponsors the enterprise AI platform initiative.",
                  subject="person-a", obj="initiative-1" if pathway == "STRATEGIC_EXPLORATION" else "req-123")])
    return r


class CorePathwayTests(unittest.TestCase):
    def test_t01_ai_initiative_is_not_hiring(self):
        o = evaluate_opportunity(sample())
        self.assertEqual(o["research_state"], "ASSESSABLE")
        self.assertEqual(o["hiring_evidence"], "STRATEGIC_ACTIVITY_NO_HIRING_EVIDENCE")
        self.assertFalse(o["send_authorized"])

    def test_t02_executive_documented_ownership(self):
        o = evaluate_opportunity(sample(executive=True))
        self.assertEqual(o["engagement_readiness"], "ENGAGEMENT_REVIEW_ELIGIBLE")

    def test_t03_location_does_not_auto_promote(self):
        x = sample(); x["contribution"]["candidate_claim_approved"] = False
        self.assertEqual(evaluate_opportunity(x)["research_state"], "DISCOVERED")

    def test_t04_no_hiring_still_assessable(self):
        self.assertEqual(evaluate_opportunity(sample())["research_state"], "ASSESSABLE")

    def test_t05_unknown_ownership_does_not_invent_sponsor(self):
        self.assertIn("EXECUTIVE_OWNER_UNVERIFIED", evaluate_opportunity(sample())["reasons"])

    def test_t06_real_attributed_job_no_manager(self):
        o = evaluate_opportunity(sample("DIRECT_HIRING"))
        self.assertEqual(o["research_state"], "ASSESSABLE")
        self.assertEqual(o["manual_application"], "OWNER_AUTH_REQUIRED")
        self.assertEqual(o["engagement_readiness"], "RESEARCH_PENDING")
        self.assertEqual(o["hiring_evidence"], "ACTIVE_POSTED_ROLE")
        self.assertEqual(o["candidate_fit_status"], "REPORTED_MATCH")

    def test_active_job_evidence_survives_unknown_candidate_qualifications(self):
        x = sample("DIRECT_HIRING")
        x["job"]["mandatory_qualifications"] = [
            {"requirement": "Progressive transformation leadership", "status": "UNVERIFIED"}]
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertEqual(result["hiring_evidence"], "ACTIVE_POSTED_ROLE")
        self.assertEqual(result["candidate_fit_status"], "UNVERIFIED")
        self.assertEqual(result["manual_application"], "NOT_ELIGIBLE")

    def test_strategic_contribution_remains_a_hypothesis_status(self):
        result = evaluate_opportunity(sample())
        self.assertEqual(result["candidate_fit_status"],
                         "CONTRIBUTION_HYPOTHESIS_REPORTED")

    def test_direct_hiring_does_not_require_separate_ai_objective(self):
        x=sample("DIRECT_HIRING")
        x["initiative"]["objective_claim_id"]=None
        x["claims"]=[c for c in x["claims"] if c["claim_id"] != "objective"]
        self.assertEqual(evaluate_opportunity(x)["research_state"], "ASSESSABLE")

    def test_composite_direct_hiring_reports_all_independent_failures(self):
        """One broken vacancy must not conceal stale identity and ownership."""
        x = sample("DIRECT_HIRING", executive=True)
        x["claims"][1]["claim_text"] = "Unrelated text not found in source excerpt"
        x["claims"][-1]["object_id"] = "other-requisition"
        stale = (date.today() - timedelta(days=120)).isoformat()
        x["claims"][-2]["retrieved_at"] = stale
        x["claims"][-2]["published_on"] = stale
        x["executive"]["route"]["verified_for_person"] = False
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertEqual(result["engagement_readiness"], "NOT_PREPARED")
        self.assertTrue({
            "JOB_STATUS_UNVERIFIED",
            "EXECUTIVE_OWNERSHIP_SOURCE_MISSING",
            "CURRENT_EXECUTIVE_ROLE_UNVERIFIED",
            "NO_VERIFIED_PERSON_ROUTE",
        }.issubset(result["reasons"]))
        for key in ("contact_ready", "send_authorized", "outbound_sent",
                    "application_submitted", "private_history_checked"):
            self.assertFalse(result[key])
        self.assertEqual(result["manual_application"], "NOT_ELIGIBLE")

    def test_composite_misleading_ai_claim_accumulates_strategy_defects(self):
        x = sample("STRATEGIC_EXPLORATION", executive=True)
        x["claims"][0]["page_read_success"] = False
        x["contribution"]["leadership_need_assumed"] = True
        x["contribution"]["hiring_claim"] = True
        x["claims"][-1]["object_id"] = "unsupported-initiative"
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertEqual(result["engagement_readiness"], "NOT_PREPARED")
        self.assertTrue({
            "OBJECTIVE_NOT_SOURCE_SUPPORTED",
            "UNSUPPORTED_HIRING_CLAIM",
            "INVENTED_LEADERSHIP_GAP",
            "EXECUTIVE_OWNERSHIP_SOURCE_MISSING",
        }.issubset(result["reasons"]))
        self.assertFalse(result["send_authorized"])

    def test_valid_official_job_survives_bad_named_executive(self):
        x = sample("DIRECT_HIRING", executive=True)
        x["claims"][-1]["object_id"] = "other-requisition"
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "ASSESSABLE")
        self.assertEqual(result["engagement_readiness"], "RESEARCH_PENDING")
        self.assertIn("EXECUTIVE_OWNERSHIP_SOURCE_MISSING", result["reasons"])
        self.assertEqual(result["manual_application"], "OWNER_AUTH_REQUIRED")
        self.assertFalse(result["application_submitted"])

    def test_closed_job_collects_executive_diagnostics_without_application(self):
        x = sample("DIRECT_HIRING", executive=True)
        x["job"]["state"] = "CLOSED"
        x["claims"][-1]["object_id"] = "other-requisition"
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "CLOSED_INACTIVE")
        self.assertTrue({"JOB_CLOSED", "EXECUTIVE_OWNERSHIP_SOURCE_MISSING"}.issubset(result["reasons"]))
        self.assertEqual(result["manual_application"], "NOT_ELIGIBLE")

    def test_unread_synthetic_objective_is_evidence_hold_not_pending(self):
        """The executed Sonoran-like handoff uses canonical V2.1 state enums."""
        x = sample()
        x["capability_theme"] = "AI_STRATEGY_TRANSFORMATION"
        x["contribution"]["candidate_claim_approved"] = False
        for cid, kind, description in (
            ("objective", "BUSINESS_OBJECTIVE", "Fictional AI permit processing objective"),
            ("pilot", "PILOT", "Fictional active pilot across three offices"),
            ("funded-role", "JOB_ACTIVE", "Fictional funded executive role"),
        ):
            item = claim(cid, kind, description, url="https://synthetic.invalid/" + cid)
            item["page_read_success"] = False
            item["support_relationship"] = "NONE"
            item["excerpt"] = ""
            if cid == "objective":
                x["claims"] = [item]
            else:
                x["claims"].append(item)
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertEqual(result["engagement_readiness"], "NOT_PREPARED")
        self.assertEqual(result["owner_decision"], "NOT_REVIEWED")
        self.assertTrue({
            "OBJECTIVE_NOT_SOURCE_SUPPORTED", "UNAPPROVED_CANDIDATE_CLAIM",
            "EXECUTIVE_OWNER_UNVERIFIED",
        }.issubset(result["reasons"]))
        self.assertEqual(result["hiring_evidence"], "STRATEGIC_ACTIVITY_NO_HIRING_EVIDENCE")
        for flag in ("contact_ready", "send_authorized", "application_submitted"):
            self.assertFalse(result[flag])

    def test_missing_candidate_attestation_is_discovered_not_evidence_hold(self):
        x = sample()
        x["contribution"]["candidate_claim_approved"] = False
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "DISCOVERED")
        self.assertEqual(result["engagement_readiness"], "NOT_PREPARED")
        self.assertNotIn("OBJECTIVE_NOT_SOURCE_SUPPORTED", result["reasons"])

    def test_unsupported_strategic_hiring_assertion_is_evidence_hold(self):
        x = sample()
        x["contribution"]["hiring_claim"] = True
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertIn("UNSUPPORTED_HIRING_CLAIM", result["reasons"])
        self.assertFalse(result["application_submitted"])

    def test_mismatched_contribution_objective_is_evidence_hold(self):
        x = sample()
        x["contribution"]["business_objective_claim_id"] = "unrelated-objective"
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertIn("CONTRIBUTION_NOT_LINKED_TO_OBJECTIVE", result["reasons"])

    def test_research_state_enum_does_not_contain_engagement_readiness(self):
        from outreach_agent.career_intelligence import RESEARCH_STATES, ENGAGEMENT_STATES
        self.assertIn("DISCOVERED", RESEARCH_STATES)
        self.assertNotIn("RESEARCH_PENDING", RESEARCH_STATES)
        self.assertIn("RESEARCH_PENDING", ENGAGEMENT_STATES)

    def test_t07_closed_job(self):
        x=sample("DIRECT_HIRING"); x["job"]["state"]="CLOSED"
        result=evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "CLOSED_INACTIVE")
        self.assertEqual(result["hiring_evidence"], "EXPIRED_OR_WITHDRAWN")

    def test_t08_mature_ai_team_no_invented_gap(self):
        x=sample(); x["contribution"]["leadership_need_assumed"]=True
        self.assertIn("INVENTED_LEADERSHIP_GAP", evaluate_opportunity(x)["reasons"])

    def test_t09_title_only_not_sponsorship(self):
        x=sample(executive=True); x["executive"]["ownership"]["ownership_grade"]="FUNCTIONALLY_PLAUSIBLE"
        self.assertEqual(evaluate_opportunity(x)["engagement_readiness"], "RESEARCH_PENDING")

    def test_t10_missing_mandatory_credentials(self):
        x=sample("DIRECT_HIRING"); x["job"].pop("mandatory_qualifications")
        x["job"]["mandatory_requirements_met"]=False
        self.assertIn("MANDATORY_QUALIFICATION_UNVERIFIED", evaluate_opportunity(x)["reasons"])

    def test_mandatory_qualification_gap_is_distinct_from_unknown(self):
        x = sample("DIRECT_HIRING")
        x["job"].pop("mandatory_requirements_met", None)
        x["job"]["mandatory_qualifications"] = [
            {"requirement": "progressive transformation leadership", "status": "GAP",
             "candidate_evidence_refs": ["candidate-profile:experience"]},
            {"requirement": "executive communication", "status": "UNVERIFIED"},
        ]
        result = evaluate_opportunity(x)
        self.assertIn("MANDATORY_QUALIFICATION_GAP", result["reasons"])
        self.assertIn("MANDATORY_QUALIFICATION_UNVERIFIED", result["reasons"])

    def test_unsubstantiated_qualification_gap_is_downgraded_to_unknown(self):
        x = sample("DIRECT_HIRING")
        x["job"].pop("mandatory_requirements_met", None)
        x["job"]["mandatory_qualifications"] = [
            {"requirement": "utility experience", "status": "GAP"},
        ]
        result = evaluate_opportunity(x)
        self.assertIn("MANDATORY_QUALIFICATION_UNVERIFIED", result["reasons"])
        self.assertNotIn("MANDATORY_QUALIFICATION_GAP", result["reasons"])
        self.assertEqual(result["candidate_fit_status"], "UNVERIFIED")

    def test_legacy_aggregate_true_does_not_verify_all_requirements(self):
        x = sample("DIRECT_HIRING")
        x["job"].pop("mandatory_qualifications")
        x["job"]["mandatory_requirements_met"] = True
        result = evaluate_opportunity(x)
        self.assertIn("MANDATORY_QUALIFICATION_UNVERIFIED", result["reasons"])
        self.assertEqual(result["qualification_assessment"][0]["status"], "UNVERIFIED")

    def test_unread_current_listing_does_not_verify_active_job(self):
        x = sample("DIRECT_HIRING")
        x["claims"][-1]["page_read_success"] = False
        result = evaluate_opportunity(x)
        self.assertIn("JOB_STATUS_UNVERIFIED", result["reasons"])
        self.assertNotIn("JOB_STATUS_STALE", result["reasons"])

    def test_missing_role_relevance_keeps_active_role_pending(self):
        x = sample("DIRECT_HIRING")
        x["job"].pop("role_relevance")
        result = evaluate_opportunity(x)
        self.assertIn("ROLE_RELEVANCE_UNVERIFIED", result["reasons"])
        self.assertEqual(result["candidate_fit_status"], "UNVERIFIED")

    def test_unknown_work_authorization_is_not_location_failure(self):
        x = sample("DIRECT_HIRING")
        x["job"]["candidate_eligibility"] = {"work_authorization": "UNVERIFIED"}
        result = evaluate_opportunity(x)
        self.assertIn("WORK_AUTHORIZATION_UNVERIFIED", result["reasons"])
        self.assertNotIn("WORK_LOCATION_INELIGIBLE", result["reasons"])

    def test_remote_and_citizenship_eligibility_are_separate(self):
        x = sample("DIRECT_HIRING")
        x["organization"]["work_mode"] = "US_REMOTE"
        x["job"]["remote_eligibility"] = "UNVERIFIED"
        x["job"]["citizenship_required"] = True
        result = evaluate_opportunity(x)
        self.assertIn("REMOTE_ELIGIBILITY_UNVERIFIED", result["reasons"])
        self.assertIn("CITIZENSHIP_UNVERIFIED", result["reasons"])
        self.assertNotIn("WORK_LOCATION_INELIGIBLE", result["reasons"])

    def test_numeric_serialized_requisition_id_matches_textual_claim_id(self):
        x = sample("DIRECT_HIRING")
        x["claims"][-1]["object_id"] = 123
        x["job"]["requisition_id"] = "123"
        self.assertEqual(evaluate_opportunity(x)["research_state"], "ASSESSABLE")

    def test_leading_zero_requisition_identity_is_preserved_exactly(self):
        x = sample("DIRECT_HIRING")
        x["job"]["requisition_id"] = "01885050"
        x["claims"][-1]["object_id"] = "01885050"
        self.assertEqual(evaluate_opportunity(x)["research_state"], "ASSESSABLE")
        x["claims"][-1]["object_id"] = 1885050
        self.assertIn("JOB_STATUS_UNVERIFIED", evaluate_opportunity(x)["reasons"])

    def test_citizenship_ineligibility_only_blocks_when_required(self):
        x = sample("DIRECT_HIRING")
        x["job"]["citizenship_required"] = False
        x["job"]["candidate_eligibility"]["citizenship"] = "INELIGIBLE"
        result = evaluate_opportunity(x)
        self.assertNotIn("CITIZENSHIP_REQUIREMENT_NOT_MET", result["reasons"])
        self.assertNotIn("CITIZENSHIP_UNVERIFIED", result["reasons"])

    def test_separate_mandates_under_one_initiative_keep_distinct_identity(self):
        a = sample()
        b = sample()
        a["contribution"]["mandate_key"] = "product-platform"
        b["contribution"]["mandate_key"] = "enterprise-transformation"
        self.assertEqual(a["initiative"]["initiative_id"], b["initiative"]["initiative_id"])
        self.assertNotEqual(opportunity_identity(a)[0], opportunity_identity(b)[0])

    def test_out_of_scope_ai_technical_role_is_excluded(self):
        x = sample("DIRECT_HIRING")
        x["job"]["role_relevance"] = "OUT_OF_SCOPE"
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EXCLUDED")
        self.assertIn("ROLE_OUTSIDE_TARGET_FUNCTION", result["reasons"])

    def test_strategic_identity_falls_back_to_stable_initiative_id(self):
        x = sample()
        x["contribution"].pop("mandate_key")
        key, reason = opportunity_identity(x)
        self.assertIsNone(reason)
        self.assertEqual(key, ("org-1", "STRATEGIC", "initiative-1", "initiative-1"))

    def test_historical_executive_mention_does_not_prove_current_ownership(self):
        x = sample(executive=True)
        old = (date.today() - timedelta(days=120)).isoformat()
        x["claims"][-1]["published_on"] = old
        result = evaluate_opportunity(x)
        self.assertIn("EXECUTIVE_OWNERSHIP_SOURCE_MISSING", result["reasons"])
        self.assertEqual(result["engagement_readiness"], "RESEARCH_PENDING")

    def test_current_role_claim_must_bind_the_target_employer(self):
        x = sample(executive=True)
        x["claims"][-2]["object_id"] = "other-employer"
        result = evaluate_opportunity(x)
        self.assertIn("CURRENT_EXECUTIVE_ROLE_UNVERIFIED", result["reasons"])
        self.assertEqual(result["engagement_readiness"], "RESEARCH_PENDING")
        self.assertFalse(result["contact_ready"])

    def test_departure_from_another_employer_is_not_this_employer_conflict(self):
        x = sample(executive=True)
        x["claims"].append(claim("old-employer-departure", "EXECUTIVE_AFFILIATION_ENDED",
                                 "The leader left a different employer.",
                                 subject="person-a", obj="other-employer"))
        result = evaluate_opportunity(x)
        self.assertEqual(result["executive_affiliation_conflict_claim_ids"], [])
        self.assertEqual(result["engagement_readiness"], "ENGAGEMENT_REVIEW_ELIGIBLE")

    def test_generic_role_report_with_explicit_conflict_link_blocks_promotion(self):
        x = sample(executive=True)
        conflict = claim("newer-public-role", "PUBLIC_ROLE_UPDATE",
                         "The executive is now listed as an independent advisor.",
                         subject="person-a", obj="org-1")
        conflict["conflicts"] = ["current-role"]
        x["claims"].append(conflict)
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertEqual(result["engagement_readiness"], "NOT_PREPARED")
        self.assertEqual(result["executive_affiliation_conflict_claim_ids"], ["newer-public-role"])
        self.assertIn("SOURCE_CONFLICT", result["reasons"])
        self.assertFalse(result["contact_ready"])

    def test_generic_conflict_without_role_reference_is_not_departure_proof(self):
        x = sample(executive=True)
        conflict = claim("different-topic", "PUBLIC_ROLE_UPDATE",
                         "The executive has a professional advisory appointment.",
                         subject="person-a", obj="org-1")
        conflict["conflicts"] = ["other-claim"]
        x["claims"].append(conflict)
        result = evaluate_opportunity(x)
        self.assertEqual(result["executive_affiliation_conflict_claim_ids"], [])
        self.assertNotIn("CURRENT_EXECUTIVE_AFFILIATION_CONFLICT", result["reasons"])

    def test_claim_linked_to_other_employer_cannot_block_current_employer(self):
        x = sample(executive=True)
        conflict = claim("other-employer", "PUBLIC_ROLE_UPDATE",
                         "The executive left a different organization.",
                         subject="person-a", obj="not-org-1")
        conflict["conflicts"] = ["current-role"]
        x["claims"].append(conflict)
        result = evaluate_opportunity(x)
        self.assertEqual(result["executive_affiliation_conflict_claim_ids"], [])

    def test_former_roche_leader_conflicts_with_outdated_official_bio(self):
        """Newer independently sourced departure blocks stale current-role promotion."""
        x = sample(executive=True)
        x["claims"][-2]["published_on"] = (date.today()-timedelta(days=400)).isoformat()
        departure = claim(
            "person-departed", "EXECUTIVE_AFFILIATION_ENDED",
            "The former digital pathology leader left the employer.",
            subject="person-a", obj="org-1",
            url="https://industry.example/2026/former-executive")
        departure["source_origin_id"] = "independent-industry"
        x["claims"].append(departure)
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertEqual(result["engagement_readiness"], "NOT_PREPARED")
        self.assertIn("SOURCE_CONFLICT", result["reasons"])
        self.assertIn("CURRENT_EXECUTIVE_AFFILIATION_CONFLICT", result["reasons"])
        self.assertEqual(result["executive_affiliation_conflict_claim_ids"], ["person-departed"])
        self.assertFalse(result["contact_ready"])
        self.assertFalse(result["send_authorized"])

    def test_unreadable_departure_lead_still_blocks_role_promotion(self):
        x = sample(executive=True)
        x["claims"][-2]["published_on"] = "UNDATED"
        conflict = claim("departure-lead", "EXECUTIVE_AFFILIATION_ENDED",
                         "The leader has departed the employer.",
                         subject="person-a", obj="org-1")
        conflict["page_read_success"] = False
        x["claims"].append(conflict)
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "EVIDENCE_HOLD")
        self.assertIn("SOURCE_CONFLICT", result["reasons"])
        self.assertFalse(result["contact_ready"])

    def test_newer_reappointment_can_supersede_historical_departure(self):
        x = sample(executive=True)
        departure = claim("past-departure", "EXECUTIVE_AFFILIATION_ENDED",
                          "The leader previously left the employer.",
                          subject="person-a", obj="org-1")
        departure["published_on"] = (date.today()-timedelta(days=150)).isoformat()
        x["claims"].append(departure)
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "ASSESSABLE")
        self.assertEqual(result["engagement_readiness"], "ENGAGEMENT_REVIEW_ELIGIBLE")
        self.assertEqual(result["executive_affiliation_conflict_claim_ids"], [])

    def test_banner_ai_leader_and_tep_cio_are_not_automatically_initiative_owners(self):
        # Fictional structurally valid evidence mirrors the different degrees
        # of responsibility; this does not certify those real individuals.
        leader = sample(executive=True)
        banner = evaluate_opportunity(leader)
        self.assertEqual(banner["research_state"], "ASSESSABLE")
        self.assertEqual(banner["engagement_readiness"], "ENGAGEMENT_REVIEW_ELIGIBLE")
        self.assertEqual(banner["source_assurance"],
                         "SELF_REPORTED_STRUCTURAL_METADATA_NOT_INDEPENDENTLY_WEB_VERIFIED")
        tep = sample(executive=True)
        tep["executive"]["ownership"]["ownership_grade"] = "FUNCTIONALLY_PLAUSIBLE"
        it = evaluate_opportunity(tep)
        self.assertIn("EXECUTIVE_OWNER_UNVERIFIED", it["reasons"])
        self.assertEqual(it["research_state"], "ASSESSABLE")
        self.assertEqual(it["engagement_readiness"], "RESEARCH_PENDING")

    def test_independent_job_route_survives_a_disputed_manager(self):
        x = sample("DIRECT_HIRING", executive=True)
        x["claims"][-2]["published_on"] = "UNDATED"
        x["claims"].append(claim("left-employer", "EXECUTIVE_AFFILIATION_ENDED",
                                 "The named manager left the company.",
                                 subject="person-a", obj="org-1"))
        result = evaluate_opportunity(x)
        self.assertEqual(result["research_state"], "ASSESSABLE")
        self.assertEqual(result["engagement_readiness"], "RESEARCH_PENDING")
        self.assertIn("SOURCE_CONFLICT", result["reasons"])
        self.assertEqual(result["manual_application"], "OWNER_AUTH_REQUIRED")
        self.assertFalse(result["application_submitted"])

    def test_t11_prior_meeting_does_not_merge_opportunities(self):
        a,b=sample(),sample(); b["initiative"]["initiative_id"]="initiative-2"
        self.assertNotEqual(opportunity_identity(a)[0], opportunity_identity(b)[0])

    def test_t12_all_rejected_no_quota(self):
        x=sample(); o=evaluate_opportunity(x)
        r=assess_owner_feedback({"decision":"REJECT","reason":"No meaningful contribution"},o)
        self.assertEqual(r["owner_decision"],"REJECT")
        self.assertFalse(r["contact_ready"])

    def test_t13_owner_interest_cannot_create_route(self):
        r=assess_owner_feedback({"decision":"PURSUE","reason":"Tucson"},evaluate_opportunity(sample()))
        self.assertEqual(r["engagement_readiness"],"RESEARCH_PENDING")
        self.assertFalse(r["send_authorized"])

    def test_t14_url_alone_insufficient(self):
        x=sample();x["claims"][0]["page_read_success"]=False
        self.assertEqual(evaluate_opportunity(x)["research_state"],"EVIDENCE_HOLD")

    def test_t15_unverified_ownership_quote(self):
        x=sample(executive=True);x["claims"][-1]["object_id"]="other-program"
        self.assertIn("EXECUTIVE_OWNERSHIP_SOURCE_MISSING",evaluate_opportunity(x)["reasons"])

    def test_t16_owner_private_discussion_does_not_create_public_job(self):
        x=sample();x["contribution"]["hiring_claim"]=True
        self.assertIn("UNSUPPORTED_HIRING_CLAIM",evaluate_opportunity(x)["reasons"])

    def test_t17_two_requisitions_are_distinct(self):
        a,b=sample("DIRECT_HIRING"),sample("DIRECT_HIRING")
        b["job"]["requisition_id"]="req-456"
        self.assertNotEqual(opportunity_identity(a)[0],opportunity_identity(b)[0])

    def test_t18_name_only_cannot_resolve_duplicate(self):
        a=sample("DIRECT_HIRING");a["job"]["requisition_id"]=""
        self.assertEqual(opportunity_identity(a)[1],"IDENTITY_COLLISION_HOLD")

    def test_t19_opt_out_applies_person_only(self):
        x=sample("DIRECT_HIRING",executive=True);x["executive"]["opted_out"]=True
        y=evaluate_opportunity(x)
        self.assertEqual(y["engagement_readiness"],"SUPPRESSED")
        self.assertEqual(y["manual_application"],"OWNER_AUTH_REQUIRED")

    def test_t20_wrong_project_is_excluded(self):
        x=sample();x["project_id"]="NOVA_SUBCONTRACTING"
        self.assertEqual(evaluate_opportunity(x)["research_state"],"EXCLUDED")

    def test_t21_current_job_without_supporting_claim_is_hold(self):
        x=sample("DIRECT_HIRING");x["claims"][-1]["claim_text"]="Other text not in passage"
        self.assertIn("JOB_STATUS_UNVERIFIED",evaluate_opportunity(x)["reasons"])

    def test_t22_outdated_job_status_is_hold(self):
        x=sample("DIRECT_HIRING");x["claims"][-1]["retrieved_at"]=(date.today()-timedelta(days=15)).isoformat()
        x["claims"][-1]["published_on"]=(date.today()-timedelta(days=15)).isoformat()
        self.assertIn("JOB_STATUS_STALE",evaluate_opportunity(x)["reasons"])

    def test_t23_duplicate_evidence_claim_id(self):
        x=sample();x["claims"].append(copy.deepcopy(x["claims"][0]))
        self.assertIn("DUPLICATE_CLAIM_ID",evaluate_opportunity(x)["reasons"])

    def test_t24_invalid_current_role(self):
        x=sample(executive=True);x["claims"][-2]["support_relationship"]="CONTEXT_ONLY"
        self.assertIn("CURRENT_EXECUTIVE_ROLE_UNVERIFIED",evaluate_opportunity(x)["reasons"])

    def test_t25_general_contact_form_is_not_person_specific(self):
        x=sample(executive=True);x["executive"]["route"]["route_type"]="INDIRECT_GENERAL"
        self.assertIn("NO_VERIFIED_PERSON_ROUTE",evaluate_opportunity(x)["reasons"])

    def test_t26_undated_original_source_still_needs_human_verification(self):
        x=sample();x["claims"][0]["published_on"]="UNDATED"
        self.assertEqual(evaluate_opportunity(x)["source_assurance"],
                         "SELF_REPORTED_STRUCTURAL_METADATA_NOT_INDEPENDENTLY_WEB_VERIFIED")

    def test_t27_missing_candidate_basis(self):
        x=sample();x["contribution"]["candidate_basis"]="tiny"
        self.assertIn("CANDIDATE_BASIS_MISSING",evaluate_opportunity(x)["reasons"])

    def test_t28_research_feedback_does_not_send(self):
        x=sample();r=assess_owner_feedback({"decision":"RESEARCH_MORE","reason":"Find business owner"},evaluate_opportunity(x))
        self.assertFalse(r["outbound_sent"])

    def test_t29_identity_missing_is_held(self):
        x=sample();x["organization"]["organization_id"]=""
        self.assertEqual(opportunity_identity(x)[1],"IDENTITY_COLLISION_HOLD")

    def test_t30_source_date_future_invalid(self):
        x=sample();x["claims"][0]["retrieved_at"]=(date.today()+timedelta(days=2)).isoformat()
        self.assertIn("OBJECTIVE_NOT_SOURCE_SUPPORTED",evaluate_opportunity(x)["reasons"])

    def test_t31_application_is_not_submission(self):
        r=evaluate_opportunity(sample("DIRECT_HIRING"))
        self.assertFalse(r["application_submitted"])

    def test_t32_gap_cannot_be_scored_away(self):
        x=sample();x["score_total"]=100
        x["contribution"]["candidate_claim_approved"]=False
        self.assertEqual(evaluate_opportunity(x)["research_state"],"DISCOVERED")

    def test_t33_two_employers_separate(self):
        a,b=sample(),sample();b["organization"]["organization_id"]="org-2"
        self.assertNotEqual(opportunity_identity(a)[0],opportunity_identity(b)[0])

    def test_t34_empty_packet_is_honest(self):
        a=audit_packet([])
        self.assertEqual(a["reviewed"],0)
        self.assertEqual(a["new_contact_ready"],0)

    def test_audit_duplicate_opportunity(self):
        p=audit_packet([sample(),sample()])
        self.assertEqual(p["identity_holds"],[0,1])

    def test_collision_blocks_batch_engagement(self):
        r=audit_packet([sample(),sample()])
        self.assertEqual(r["research_states"].get("EVIDENCE_HOLD"),2)
        self.assertEqual(r["results"][0]["engagement_readiness"],"NOT_PREPARED")

    def test_six_case_audit_preserves_closed_and_rejected_controls(self):
        records = [sample("DIRECT_HIRING") for _ in range(6)]
        for i, record in enumerate(records):
            record["organization"]["organization_id"] = f"org-{i}"
            record["organization"]["name"] = f"Employer {i}"
            record["initiative"]["initiative_id"] = f"initiative-{i}"
            record["job"]["requisition_id"] = f"req-{i}"
            record["claims"][-1]["object_id"] = f"req-{i}"
        records[1]["job"]["state"] = "CLOSED"
        records[2]["job"]["role_relevance"] = "OUT_OF_SCOPE"
        result = audit_packet(records)
        self.assertEqual(result["reviewed"], 6)
        self.assertEqual(result["results"][1]["research_state"], "CLOSED_INACTIVE")
        self.assertEqual(result["results"][2]["research_state"], "EXCLUDED")
        self.assertEqual(result["results"][5]["organization_id"], "org-5")
        self.assertEqual(result["results"][5]["opportunity_identity"],
                         ("org-5", "ATS", "req-5"))
        self.assertEqual(result["identity_holds"], [])

    def test_stale_current_executive_role_is_not_verified(self):
        x=sample(executive=True)
        old=(date.today()-timedelta(days=120)).isoformat()
        x["claims"][-2]["retrieved_at"]=old
        x["claims"][-2]["published_on"]=old
        self.assertIn("CURRENT_EXECUTIVE_ROLE_UNVERIFIED",evaluate_opportunity(x)["reasons"])

    def test_documented_owner_with_missing_route_is_hold(self):
        x=sample(executive=True);x["executive"]["route"]["verified_for_person"]=False
        self.assertEqual(evaluate_opportunity(x)["engagement_readiness"],"RESEARCH_PENDING")

    def test_owner_decision_does_not_verify_fact(self):
        r=assess_owner_feedback({"decision":"PURSUE","reason":"Product leadership"},
                                 evaluate_opportunity(sample()))
        self.assertIn("NOT_INDEPENDENTLY_WEB_VERIFIED",r["source_assurance"])

    def test_never_source_truth_claim(self):
        self.assertFalse(evaluate_opportunity(sample(executive=True))["contact_ready"])

    def test_no_sends_for_all_eligible_paths(self):
        for x in (sample(),sample(executive=True),sample("DIRECT_HIRING"),
                  sample("DIRECT_HIRING",executive=True)):
            self.assertFalse(evaluate_opportunity(x)["send_authorized"])

if __name__ == "__main__":
    unittest.main()
