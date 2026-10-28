"""Structural policy regression tests; NOT evidence of live governance enforcement."""
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from validate_governance import validate_governance

DOC_PATHS = (
    "config/operating-policy.json",
    "docs/PRODUCTION_PLAN.md",
    "README.md",
    "AGENTS.md",
    "references/private-memory-contract.md",
    ".agents/skills/relationship-memory/SKILL.md",
    "docs/OPERATING_RUNBOOK.md",
)

class GovernanceAlignmentTests(unittest.TestCase):
    def test_current_contract_is_consistent(self):
        self.assertEqual(validate_governance(), [])

    def test_autonomous_sending_cannot_be_enabled_without_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in DOC_PATHS:
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, target)
            policy = root / "config/operating-policy.json"
            data = json.loads(policy.read_text(encoding="utf-8"))
            data["outreach"]["automatic_sending"] = True
            data["governance"]["codex_direct_dpapi_access_prohibited"] = False
            policy.write_text(json.dumps(data), encoding="utf-8")
            errors = validate_governance(root)
            self.assertIn("automatic sending must remain forbidden", errors)
            self.assertIn("governance requirement disabled: codex_direct_dpapi_access_prohibited", errors)

    def test_private_memory_instruction_cannot_permit_direct_codex_lookup(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in DOC_PATHS:
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, target)
            contract = root / "references/private-memory-contract.md"
            contract.write_text(contract.read_text(encoding="utf-8") +
                                "\nCodex may call scripts/relationship-check.ps1 directly.\n",
                                encoding="utf-8")
            self.assertIn("private-memory contract permits direct Codex DPAPI lookup",
                          validate_governance(root))

    def test_memory_and_release_gates_cannot_be_removed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in DOC_PATHS:
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, target)
            policy = root / "config/operating-policy.json"
            data = json.loads(policy.read_text(encoding="utf-8"))
            data["memory"]["codex_access"] = "unrestricted"
            data["production_release_gates"].remove("trusted_private_memory_batch_reconciliation")
            policy.write_text(json.dumps(data), encoding="utf-8")
            errors = validate_governance(root)
            self.assertIn("Codex memory access policy drift", errors)
            self.assertIn("missing mandatory production-release gates", errors)

    def test_authorization_rule_cannot_be_switched_on_without_failure(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            for rel in DOC_PATHS:
                target = root / rel
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(ROOT / rel, target)
            policy = root / "config/operating-policy.json"
            data = json.loads(policy.read_text(encoding="utf-8"))
            data["governance"]["send_authorization_gate_status"] = "ALLOW"
            policy.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("send authorization policy must remain blocked until implementation",
                          validate_governance(root))

if __name__ == "__main__":
    unittest.main()
