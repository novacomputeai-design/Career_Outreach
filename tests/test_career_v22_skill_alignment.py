"""All fourteen skill instructions must share the safe V2.2 opt-in boundary."""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SKILLS={
 "contact-verification","conversation-preparation","daily-executive-brief",
 "daily-executive-outreach","discovery-strategy-optimization","follow-up-planning",
 "leadership-discovery","organization-discovery","outcome-intelligence",
 "outreach-drafting","provenance-and-freshness","relationship-memory",
 "relationship-qualification","run-quality-audit",
}

class V22SkillAlignmentTests(unittest.TestCase):
    def test_all_fourteen_versioned_skills_document_pilot_scope(self):
        actual={p.parent.name for p in (ROOT/".agents"/"skills").glob("*/SKILL.md")}
        self.assertEqual(actual,SKILLS)
        for name in SKILLS:
            text=(ROOT/".agents"/"skills"/name/"SKILL.md").read_text(encoding="utf-8")
            self.assertIn("career-intelligence-operating-contract-v2.2.md",text,name)
            self.assertIn("supervised opt-in only",text,name)
            self.assertIn("production authority",text,name)

    def test_mastering_and_contract_are_separate_from_v21(self):
        self.assertTrue((ROOT/"docs/CAREER_V22_MASTERING_GATES.md").is_file())
        self.assertTrue((ROOT/"references/career-intelligence-operating-contract-v2.2.md").is_file())
        self.assertTrue((ROOT/"references/career-intelligence-operating-contract-v2.1.md").is_file())

    def test_native_host_and_private_review_not_faked(self):
        from outreach_agent.skill_trace import audit_skill_trace
        records={name:{"state":"NOT_VERIFIED"} for name in SKILLS}
        result=audit_skill_trace(records)
        self.assertTrue(result["structural_pass"])
        self.assertFalse(result["independent_native_execution_verified"])

if __name__=="__main__":
    unittest.main()
