"""V2.2 host handoff order, artifact binding and safety negative cases."""
import copy
import unittest
from outreach_agent.career_handoff import STAGES, audit_research_handoffs


def chain():
    return [
        {"stage":name, "state":"REPORTED_COMPLETED",
         "input_digest": ("%064x" % (i+1)), "output_digest":("%064x" % (i+2))}
        for i,name in enumerate(STAGES)
    ]

class HandoffAuditTests(unittest.TestCase):
    def test_complete_digest_chain_is_structural_only(self):
        r=audit_research_handoffs(chain())
        self.assertTrue(r["structural_handoff_complete"])
        self.assertFalse(r["native_codex_invocation_verified"])
        self.assertFalse(r["source_truth_independently_verified"])
        self.assertFalse(r["contact_ready"])

    def test_missing_specialist_handoff_fails(self):
        x=chain();x[1]["state"]="NOT_VERIFIED"
        self.assertFalse(audit_research_handoffs(x)["structural_handoff_complete"])

    def test_reordered_stages_rejected(self):
        x=chain();x[1],x[2]=x[2],x[1]
        with self.assertRaises(ValueError):
            audit_research_handoffs(x)

    def test_digest_mismatch_detected(self):
        x=chain();x[4]["input_digest"]="f"*64
        self.assertIn("person_access:BROKEN_STAGE_HANDOFF",
                      audit_research_handoffs(x)["problems"])

    def test_required_stage_cannot_be_skipped(self):
        x=chain()
        x[1]["state"]="SKIPPED_NOT_APPLICABLE"
        x[1]["reason"]="cannot read employer page"
        x[1]["output_digest"]=x[1]["input_digest"]
        self.assertIn("provenance_review:REQUIRED_STAGE_SKIPPED",
                      audit_research_handoffs(x)["problems"])

    def test_optional_route_stage_can_be_skipped_with_reason(self):
        x=chain()
        x[4]["state"]="SKIPPED_NOT_APPLICABLE"
        x[4]["reason"]="DIRECT_HIRING official ATS route; no executive target"
        x[4]["output_digest"]=x[4]["input_digest"]
        x[5]["input_digest"]=x[4]["output_digest"]
        a=audit_research_handoffs(x)
        self.assertTrue(a["structural_handoff_complete"])
        self.assertFalse(a["send_authorized"])

if __name__=="__main__":
    unittest.main()
