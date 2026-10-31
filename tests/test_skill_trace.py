"""V2.1 conditional activation structural safeguards; not real native Codex."""
import unittest
from outreach_agent.skill_trace import ALL, ALWAYS, required_skills, audit_skill_trace


class SkillTraceTests(unittest.TestCase):
    def complete(self, required):
        return {name: ({"state": "HOST_REPORTED_NATIVE", "activation_evidence": "synthetic-host-claim"}
                       if name in required else
                       {"state": "SKIPPED_NOT_APPLICABLE", "reason": "Not requested in synthetic case"})
                for name in ALL}

    def test_all_fourteen_accounted_for(self):
        self.assertEqual(len(ALL),14)
        r=audit_skill_trace(self.complete(ALWAYS))
        self.assertTrue(r["structural_pass"])
        self.assertTrue(r["all_skills_covered"])
        self.assertFalse(r["independent_native_execution_verified"])

    def test_required_cannot_be_skipped(self):
        x=self.complete(ALWAYS)
        x["organization-discovery"]={"state":"SKIPPED_NOT_APPLICABLE","reason":"ignored"}
        self.assertIn("organization-discovery",audit_skill_trace(x)["invalid"])

    def test_conditional_not_applicable_is_valid(self):
        r=audit_skill_trace(self.complete(ALWAYS))
        self.assertTrue(r["structural_pass"])

    def test_missing_required_is_flagged(self):
        x=self.complete(ALWAYS); x.pop("run-quality-audit")
        self.assertIn("run-quality-audit",audit_skill_trace(x)["missing"])

    def test_actual_person_conversation_path(self):
        opts={"named_executive":True,"person_contact_review":True,
              "draft_requested":True,"planned_meeting":True,
              "existing_followup":True,"feedback_or_outcomes":True}
        q=required_skills(**opts)
        self.assertEqual(q,ALL)
        r=audit_skill_trace(self.complete(q),**opts)
        self.assertTrue(r["structural_pass"])
        self.assertFalse(r["independent_native_execution_verified"])

    def test_native_claim_without_evidence_fails(self):
        x=self.complete(ALWAYS);x["organization-discovery"]={"state":"HOST_REPORTED_NATIVE"}
        self.assertIn("organization-discovery",audit_skill_trace(x)["invalid"])


if __name__=="__main__":
    unittest.main()
