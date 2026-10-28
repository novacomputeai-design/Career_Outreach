"""Do not label mere operator review events as confirmed NEW/contact-ready."""
import io
import json
import unittest
from contextlib import redirect_stdout
from unittest.mock import MagicMock, patch

from outreach_agent.cli import main

class ReadinessReportTests(unittest.TestCase):
    def test_operator_reviews_cannot_inflate_confirmed_new_count(self):
        store = MagicMock()
        store.reviewed_for_run.return_value = 18
        buf = io.StringIO()
        with patch("outreach_agent.cli.PrivateStore", return_value=store), redirect_stdout(buf):
            main(["--db", "synthetic-private-path.sqlite", "run-readiness",
                  "--run-id", "synthetic-run"])
        report = json.loads(buf.getvalue())
        self.assertEqual(report["run_id"], "synthetic-run")
        self.assertEqual(report["recorded_source_route_fit_reviews"], 18)
        self.assertEqual(report["new_contact_ready"], 0)
        self.assertEqual(report["production_verified_contact_ready"], 0)
        self.assertEqual(report["novelty_verification"], "UNVERIFIED")
        self.assertIn("HOLD", report["contact_ready_gate"])
        self.assertEqual(report["messages_sent"], 0)
        self.assertNotIn("human_reviewed_contact_ready", report)
        store.close.assert_called_once()

    def test_zero_reviews_are_not_fabricated(self):
        store = MagicMock()
        store.reviewed_for_run.return_value = 0
        buf = io.StringIO()
        with patch("outreach_agent.cli.PrivateStore", return_value=store), redirect_stdout(buf):
            main(["--db", "synthetic-private-path.sqlite", "run-readiness",
                  "--run-id", "empty-synthetic-run"])
        report = json.loads(buf.getvalue())
        self.assertEqual(report["recorded_source_route_fit_reviews"], 0)
        self.assertEqual(report["new_contact_ready"], 0)

if __name__ == "__main__":
    unittest.main()
