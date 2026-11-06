"""Static safety/structure checks for focused career people-finding skills.
These tests do NOT execute Codex, validate public sources or grant outreach authority.
"""
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / ".agents" / "skills"

def skill(name):
    return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

class FocusedPersonDiscoveryContractTests(unittest.TestCase):
    def test_scope_mode_and_leadership_trigger(self):
        s = skill("daily-executive-outreach")
        for text in ("FIXED_EMPLOYER/FIXED_REQUISITION", "BROAD_DISCOVERY",
                     "even when the hiring manager is unnamed", "STRATEGIC_EXPLORATION",
                     "FIRST_CONVERSATION_TARGET", "operator-only encrypted relationship"):
            self.assertIn(text, s)

    def test_discover_before_narrowing(self):
        s = skill("leadership-discovery")
        steps = ["1. **Discover:**", "2. **Verify and classify:**",
                 "3. **Compare after searching:**", "4. **Handoff:**",
                 "5. **Report honestly:**"]
        positions = [s.index(step) for step in steps]
        self.assertEqual(sorted(positions), positions)
        for text in ("NOT a candidate search limit", "fourth person",
                     "two-person limit applies to final recommendations only",
                     "ROLE_SPECIFIC_PROMOTER", "RECRUITING_PROCESS_CONTACT"):
            self.assertIn(text, s)

    def test_direct_hiring_is_not_speculative_leadership(self):
        s = skill("relationship-qualification")
        for text in ("DIRECT_HIRING", "STRATEGIC_EXPLORATION",
                     "Do not require an additional hypothetical leadership role",
                     "mandatory experience", "does **not** waive existing scoring"):
            self.assertIn(text, s)

    def test_role_promotion_invitation_and_route_are_separate(self):
        s = skill("contact-verification")
        for text in ("ROLE_SPECIFIC_PROMOTION_ONLY", "ROLE_SPECIFIC_INVITATION_PUBLIC",
                     'apply today', "contact me about this role",
                     "HISTORICAL_PERSON_WORK_CONTACT_RECHECK", "PROFILE_ONLY",
                     "OFFICIAL_APPLICATION_ROUTE", "CONTACT_HOLD"):
            self.assertIn(text, s)
        self.assertIn("report the actual official/professional/institutional", skill("run-quality-audit"))
        self.assertIn("PROMISING_RESEARCH_ONLY", skill("daily-executive-brief"))

    def test_existing_governance_gates_remain(self):
        policy = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
        self.assertIn("operator-only", policy)
        self.assertIn("SEND_AUTHORIZED", policy)
        self.assertIn("not production-qualified", (ROOT / "references" / "daily-operating-contract.md").read_text(encoding="utf-8").lower())

    def test_behavioral_scenarios_are_unexecuted(self):
        data = json.loads((ROOT / "evals/focused_person_discovery_acceptance.json").read_text(encoding="utf-8"))
        self.assertEqual(data["assurance"], "NOT_EXECUTED_BEHAVIORAL_SCENARIOS")
        self.assertEqual(len(data["cases"]), 5)
        self.assertEqual(len({c["id"] for c in data["cases"]}), 5)
        for c in data["cases"]:
            self.assertTrue(c["scenario"] and c["must"] and c["mustNot"])
            self.assertNotIn("result", c)
            self.assertNotIn("pass", c)

if __name__ == "__main__":
    unittest.main()
