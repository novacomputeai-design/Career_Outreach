"""Windows PowerShell wrapper syntax only. No DPAPI secrets or owner data loaded."""
import os
import shutil
import subprocess
import unittest
from pathlib import Path


ROOT=Path(__file__).resolve().parents[1]


class OwnerWrapperSyntaxTests(unittest.TestCase):
    def test_python_owner_cli_compiles_without_windows_secrets(self):
        path=ROOT/"scripts"/"owner_career_v22_handoff.py"
        compile(path.read_text(encoding="utf-8"), str(path), "exec")

    @unittest.skipUnless(os.name=="nt", "PowerShell AST check on Windows only")
    def test_owner_wrapper_parses_without_execution(self):
        pwsh=shutil.which("pwsh") or shutil.which("powershell")
        self.assertIsNotNone(pwsh,"Windows owner script parser unavailable")
        target=(ROOT/"scripts"/"owner-career-v22.ps1").as_posix()
        code=(
            "$errors=$null; "
            "$tokens=$null; "
            "[System.Management.Automation.Language.Parser]::ParseFile("
            "'"+target+"',[ref]$tokens,[ref]$errors) | Out-Null; "
            "if ($errors.Count -gt 0) {$errors | Out-String | Write-Error; exit 1}"
        )
        result=subprocess.run([pwsh,"-NoProfile","-NonInteractive","-Command",code],
                              capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)
