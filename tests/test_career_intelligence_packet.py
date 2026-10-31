"""V2.1 research packet and end-to-end synthetic workflow smoke tests."""
import unittest
from datetime import date
from outreach_agent.career_intelligence_packet import build_review_packet
from outreach_agent.career_intelligence import evaluate_opportunity, audit_packet
from test_career_intelligence import sample


class PacketTests(unittest.TestCase):
    def pack(self, items=None):
        return {"schema_version": "2.1", "project_id": "PERSONAL_CAREER_OUTREACH",
                "run_id": "synthetic-001", "date_local": date.today().isoformat(),
                "opportunities": [] if items is None else items}

    def test_zero_opportunities_is_honest(self):
        p = build_review_packet(self.pack())
        self.assertEqual(p["research_summary"]["reviewed"], 0)
        self.assertEqual(p["contact_ready"], 0)

    def test_reject_private_fields_recursively(self):
        q=sample()
        q["contribution"]["private_email"]="private@example.test"
        with self.assertRaises(ValueError):
            build_review_packet(self.pack([q]))

    def test_reject_wrong_project(self):
        q=self.pack();q["project_id"]="NOVA_SUBCONTRACTING"
        with self.assertRaises(ValueError):
            build_review_packet(q)

    def test_legacy_person_packet_does_not_mix(self):
        with self.assertRaises(ValueError):
            build_review_packet({"project_id":"PERSONAL_CAREER_OUTREACH","candidates":[]})

    def test_rehearsal_strategic_sponsor(self):
        r=build_review_packet(self.pack([sample(executive=True)]))
        x=r["research_summary"]["results"][0]
        self.assertEqual(x["engagement_readiness"], "ENGAGEMENT_REVIEW_ELIGIBLE")
        self.assertFalse(x["send_authorized"])
        self.assertFalse(r["native_skills_verified"])

    def test_rehearsal_direct_ats_without_manager(self):
        r=build_review_packet(self.pack([sample("DIRECT_HIRING")]))
        x=r["research_summary"]["results"][0]
        self.assertEqual(x["manual_application"], "OWNER_AUTH_REQUIRED")
        self.assertEqual(r["applications_submitted"],0)

    def test_rehearsal_adversarial_stale_job(self):
        x=sample("DIRECT_HIRING")
        x["job"]["state"]="CLOSED"
        r=build_review_packet(self.pack([x]))
        self.assertEqual(r["research_summary"]["results"][0]["research_state"],"CLOSED_INACTIVE")
        self.assertEqual(r["outbound_sent"],0)


if __name__ == "__main__":
    unittest.main()
