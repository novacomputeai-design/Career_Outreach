"""Executable synthetic case-runner contract tests; artifacts stay outside Git."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_career_v22_e2e import MATRIX, ROOT, run_cases


class V22E2ERunnerTests(unittest.TestCase):
    def test_cli_cases_emit_machine_checkable_separate_register(self):
        original = MATRIX.read_bytes()
        with tempfile.TemporaryDirectory() as scratch:
            result_path = Path(scratch) / "results.json"
            result = run_cases(result_path, ["E2E-01", "E2E-04", "E2E-07", "E2E-13", "E2E-16"])
            self.assertTrue(result_path.exists())
            self.assertNotIn(str(ROOT).lower(), str(result_path.resolve()).lower())
            by_id = {x["case_id"]: x for x in result["case_results"]}
            for case_id in ("E2E-01", "E2E-04", "E2E-07", "E2E-13", "E2E-16"):
                self.assertEqual(by_id[case_id]["status"], "PASS", case_id)
            for item in result["case_results"]:
                self.assertEqual(item["assurance_level"], "SYNTHETIC_CLI")
                self.assertFalse(item["live_host_qualified"])
                self.assertEqual(len(item["input_digest_sha256"]), 64)
                if item["actual_observation"]["returncode"] == 0:
                    self.assertTrue(Path(item["evidence_reference"]["cli_output"]).exists())
                else:
                    self.assertIn("V2.2_SCHEMA_INVALID", item["actual_observation"]["stderr"])
        self.assertEqual(MATRIX.read_bytes(), original)

    def test_original_sixteen_cases_hardened_and_holds_honest(self):
        original = MATRIX.read_bytes()
        with tempfile.TemporaryDirectory() as scratch:
            output = Path(scratch) / "sixteen.json"
            result = run_cases(output)
            by_id = {item["case_id"]: item for item in result["case_results"]}
            self.assertEqual(set(by_id), {f"E2E-{i:02}" for i in range(1, 17)})
            self.assertEqual(
                {cid for cid, item in by_id.items() if item["status"] == "HOLD"},
                {"E2E-05", "E2E-06", "E2E-08", "E2E-15"},
            )
            self.assertEqual(
                {cid for cid, item in by_id.items() if item["status"] == "FAIL"},
                set(), {cid: x["actual_observation"] for cid, x in by_id.items() if x["status"] == "FAIL"}
            )
            for cid in ("E2E-02", "E2E-03", "E2E-11", "E2E-16"):
                item = by_id[cid]
                self.assertEqual(item["status"], "PASS")
                self.assertNotEqual(item["actual_observation"]["contribution_quality"], "STRONG_CONTRIBUTION")
                self.assertFalse(item["live_host_qualified"])
            for item in by_id.values():
                self.assertFalse(item["source_truth_independently_verified"])
                self.assertEqual(len(item["input_digest_sha256"]), 64)
        self.assertEqual(MATRIX.read_bytes(), original)

    def test_extended_source_continuity_safety_cases_have_honest_assurance(self):
        original = MATRIX.read_bytes()
        with tempfile.TemporaryDirectory() as scratch:
            result = run_cases(
                Path(scratch) / "extended.json",
                [f"E2E-{i:02}" for i in range(17, 52)],
            )
            by_id = {x["case_id"]: x for x in result["case_results"]}
            observed_synthetic = {
                "E2E-17", "E2E-18", "E2E-24", "E2E-25",
                "E2E-28", "E2E-32", "E2E-33",
                "E2E-39", "E2E-40", "E2E-43", "E2E-44", "E2E-47",
            }
            self.assertEqual(len(by_id), 35)
            self.assertEqual(
                {cid for cid, entry in by_id.items() if entry["status"] == "PASS"},
                observed_synthetic,
                {cid: entry["actual_observation"] for cid, entry in by_id.items()
                 if entry["status"] == "FAIL"},
            )
            self.assertEqual(
                {cid for cid, entry in by_id.items() if entry["status"] == "HOLD"},
                set(by_id) - observed_synthetic,
            )
            for cid, entry in by_id.items():
                self.assertFalse(entry["live_host_qualified"])
                self.assertFalse(entry["source_truth_independently_verified"])
                self.assertEqual(len(entry["input_digest_sha256"]), 64)
                if entry["status"] == "HOLD":
                    self.assertEqual(entry["assurance_level"], "SYNTHETIC_CLI_LIMITED_ASSERTION")
                    self.assertGreater(len(entry["actual_observation"]["assertion"]), 70)
        self.assertEqual(MATRIX.read_bytes(), original)

    def test_result_register_path_must_be_external(self):
        with self.assertRaisesRegex(ValueError, "RESULT_REGISTER_MUST_BE_OUTSIDE_REPOSITORY"):
            run_cases(ROOT / "evals" / "forbidden.json", ["E2E-01"])


if __name__ == "__main__":
    unittest.main()
