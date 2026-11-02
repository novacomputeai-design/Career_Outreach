"""Public opportunity packet isolation and non-overwrite regression."""
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from outreach_agent.opportunity_packet import build_opportunity_report, assess_private_file
from test_opportunity_qualification import case


def packet(records):
    return {"schema_version": "1.1",
            "project_id": "PERSONAL_CAREER_OUTREACH",
            "run_id": "organization-first-pilot-001",
            "date_local": date.today().isoformat(),
            "opportunities": records}


class OpportunityPacketTests(unittest.TestCase):
    def test_explicit_report_is_unapproved(self):
        r = build_opportunity_report(packet([case()]))
        self.assertEqual(r["opportunities_researched"], 1)
        self.assertEqual(r["portfolio"]["shortfall"], 4)
        self.assertEqual(r["new_contact_ready"], 0)
        self.assertFalse(r["private_history_checked"])
        self.assertFalse(r["independent_source_truth_verified"])

    def test_empty_batch_honest_shortfall(self):
        r = build_opportunity_report(packet([]))
        self.assertEqual((r["portfolio"]["shortfall"], r["new_contact_ready"]), (5, 0))

    def test_unknown_top_level_fields_rejected(self):
        x = packet([case()])
        x["emails"] = "not allowed"
        with self.assertRaisesRegex(ValueError, "Exact"):
            build_opportunity_report(x)

    def test_scope_and_invalid_schema_rejected(self):
        x = packet([case()])
        x["project_id"] = "NOVA_SUBCONTRACTING"
        with self.assertRaisesRegex(ValueError, "Wrong"):
            build_opportunity_report(x)

    def test_output_nonoverwrite_and_sha(self):
        with tempfile.TemporaryDirectory() as root:
            source = Path(root) / "public-research.json"
            output = Path(root) / "report.json"
            source.write_text(json.dumps(packet([case()])), encoding="utf-8")
            r = assess_private_file(source, output)
            self.assertEqual(len(r["input_sha256"]), 64)
            self.assertTrue(output.is_file())
            self.assertFalse(json.loads(output.read_text())["private_history_checked"])
            with self.assertRaises(FileExistsError):
                assess_private_file(source, output)

    def test_nested_commercial_intent_fails_personal_scope(self):
        x = case()
        x["decision_maker"]["conversation_thesis"] = (
            "Submit our capability statement to the prime contractor")
        r = build_opportunity_report(packet([x]))
        self.assertEqual(r["assessments"][0]["decision"], "RESEARCH_HOLD")
        self.assertIn("CROSS_PROJECT_COMMERCIAL_OUTREACH_INTENT",
                      r["assessments"][0]["reasons"])


if __name__ == "__main__":
    unittest.main()
