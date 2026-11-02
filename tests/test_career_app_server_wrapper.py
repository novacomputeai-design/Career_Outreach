"""App Server owner-run shell syntax and safety contract checks."""
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class AppServerWrapperTests(unittest.TestCase):
    def test_owner_cli_limits(self):
        src=(ROOT/"scripts"/"career-v22-app-server.ps1").read_text(encoding="utf-8")
        self.assertIn("$gitStatus = @(& git -C $repo status --porcelain)",src)
        self.assertIn("OUTREACH_STATE_KEY",src)
        self.assertIn("OUTREACH_IDENTITY_KEY",src)
        self.assertIn("career_v22_app_server_probe.py",src)
        self.assertIn("codex.cmd",src)
        self.assertNotIn("owner-career-v22.ps1",src)
        self.assertNotIn("--full-auto",src)
        self.assertNotIn("danger-full-access",src)

    @unittest.skipUnless(os.name=="nt","PowerShell syntax verification requires Windows CI")
    def test_powershell_ast_without_executing_codex(self):
        pwsh=shutil.which("pwsh") or shutil.which("powershell")
        self.assertIsNotNone(pwsh)
        path=(ROOT/"scripts"/"career-v22-app-server.ps1").as_posix()
        expression=(
            "$e=$null;$t=$null;"
            "[System.Management.Automation.Language.Parser]::ParseFile('"+
            path+"',[ref]$t,[ref]$e)|Out-Null;"
            "if($e.Count){$e|Out-String|Write-Error;exit 1}"
        )
        p=subprocess.run([pwsh,"-NoProfile","-NonInteractive","-Command",expression],
                         capture_output=True,text=True,timeout=20)
        self.assertEqual(p.returncode,0,p.stderr)

if __name__=="__main__":
    unittest.main()
