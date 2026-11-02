"""Career opportunity learning cannot self-approve strategy changes."""
import unittest
from outreach_agent.career_owner_learning import propose_career_discovery_improvements as recommend


def event(i, decision="REJECT", reason="NO_MEANINGFUL_CONTRIBUTION"):
    return {"opportunity_identity":"opp-"+str(i), "decision":decision,"reason":reason,
            "capability_theme":"BOTH","engagement_pathway":"STRATEGIC_EXPLORATION"}


class CareerFeedbackTests(unittest.TestCase):
    def test_insufficient_data_yields_no_policy_change(self):
        x=recommend([event(1)])
        self.assertEqual(x["status"],"INSUFFICIENT_OWNER_REVIEWS")
        self.assertFalse(x["auto_applied"])

    def test_rejected_weak_contributions_propose_not_apply(self):
        x=recommend([event(i) for i in range(6)])
        self.assertEqual(x["status"],"HUMAN_REVIEW_ONLY")
        self.assertFalse(x["policy_modified"])
        self.assertTrue(all(p["requires_owner_approval"] for p in x["proposals"]))

    def test_disagreeing_reviews_do_not_force_learning(self):
        x=recommend([event(i,"PURSUE","ROLE_MATCH") for i in range(6)])
        self.assertEqual(x["status"],"NO_ACTIONABLE_PATTERN")
        self.assertEqual(x["proposals"],[])

    def test_duplicates_require_reconciliation(self):
        with self.assertRaises(ValueError):
            recommend([event(1),event(1)])

    def test_unknown_status_fails(self):
        x=event(1);x["decision"]="SEND_AUTHORIZED"
        with self.assertRaises(ValueError):
            recommend([x])

if __name__=="__main__":
    unittest.main()
