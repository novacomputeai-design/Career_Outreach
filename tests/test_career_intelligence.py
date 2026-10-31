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
                    "mandatory_requirements_met": True, "work_mode_feasible": True}
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
                  "Pat Example serves as business vice president.", subject="person-a"),
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
        self.assertEqual(evaluate_opportunity(x)["research_state"], "RESEARCH_PENDING")

    def test_t04_no_hiring_still_assessable(self):
        self.assertEqual(evaluate_opportunity(sample())["research_state"], "ASSESSABLE")

    def test_t05_unknown_ownership_does_not_invent_sponsor(self):
        self.assertIn("EXECUTIVE_OWNER_UNVERIFIED", evaluate_opportunity(sample())["reasons"])

    def test_t06_real_attributed_job_no_manager(self):
        o = evaluate_opportunity(sample("DIRECT_HIRING"))
        self.assertEqual(o["research_state"], "ASSESSABLE")
        self.assertEqual(o["manual_application"], "OWNER_AUTH_REQUIRED")
        self.assertEqual(o["engagement_readiness"], "RESEARCH_PENDING")

    def test_direct_hiring_does_not_require_separate_ai_objective(self):
        x=sample("DIRECT_HIRING")
        x["initiative"]["objective_claim_id"]=None
        x["claims"]=[c for c in x["claims"] if c["claim_id"] != "objective"]
        self.assertEqual(evaluate_opportunity(x)["research_state"], "ASSESSABLE")

    def test_t07_closed_job(self):
        x=sample("DIRECT_HIRING"); x["job"]["state"]="CLOSED"
        self.assertEqual(evaluate_opportunity(x)["research_state"], "CLOSED_INACTIVE")

    def test_t08_mature_ai_team_no_invented_gap(self):
        x=sample(); x["contribution"]["leadership_need_assumed"]=True
        self.assertIn("INVENTED_LEADERSHIP_GAP", evaluate_opportunity(x)["reasons"])

    def test_t09_title_only_not_sponsorship(self):
        x=sample(executive=True); x["executive"]["ownership"]["ownership_grade"]="FUNCTIONALLY_PLAUSIBLE"
        self.assertEqual(evaluate_opportunity(x)["engagement_readiness"], "RESEARCH_PENDING")

    def test_t10_missing_mandatory_credentials(self):
        x=sample("DIRECT_HIRING"); x["job"]["mandatory_requirements_met"]=False
        self.assertIn("MANDATORY_QUALIFICATION_GAP", evaluate_opportunity(x)["reasons"])

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
        self.assertEqual(evaluate_opportunity(x)["research_state"],"RESEARCH_PENDING")

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
        self.assertEqual(evaluate_opportunity(x)["research_state"],"RESEARCH_PENDING")

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
