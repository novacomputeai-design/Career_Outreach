"""Check read-only Codex native invocation probe syntax and safety contract."""
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]

class NativeSkillProbeTests(unittest.TestCase):
    def test_probe_disallows_working_tree_mutations_and_private_keys(self):
        s=(ROOT/"scripts"/"career-v22-native-skill-probe.ps1").read_text(encoding="utf-8")
        self.assertIn("--sandbox read-only",s)
        self.assertIn("OUTREACH_IDENTITY_KEY",s)
        self.assertIn("OUTREACH_STATE_KEY",s)
        self.assertIn("NOT_INDEPENDENTLY_VERIFIED_BY_THIS_SCRIPT",s)
        self.assertNotIn("codex exec --full-auto",s)
        self.assertNotIn("codex exec --sandbox workspace-write",s)
        self.assertIn("Get-Command codex",s)

    def test_strict_mode_git_status_is_always_array(self):
        s=(ROOT/"scripts"/"career-v22-native-skill-probe.ps1").read_text(encoding="utf-8")
        self.assertIn("$statusLines = @(& git -C $repo status --porcelain)",s)
        self.assertIn("if ($LASTEXITCODE -ne 0)",s)
        self.assertIn("if ($statusLines.Count -gt 0)",s)
        self.assertNotIn("(& git -C $repo status --porcelain).Count",s)

    @unittest.skipUnless(os.name=="nt","PowerShell native command check on Windows CI")
    def test_strict_mode_native_git_status_returns_safe_array(self):
        pwsh=shutil.which("pwsh") or shutil.which("powershell")
        self.assertIsNotNone(pwsh)
        root=str(ROOT).replace("'","''")
        code=(
            "Set-StrictMode -Version Latest;"
            "$repo='"+root+"';"
            "$statusLines=@(& git -C $repo status --porcelain);"
            "if($LASTEXITCODE -ne 0){throw 'git status failed'};"
            "if($statusLines.Count -lt 0){throw 'invalid array'};"
        )
        result=subprocess.run([pwsh,"-NoProfile","-NonInteractive","-Command",code],
                              capture_output=True,text=True,timeout=20)
        self.assertEqual(result.returncode,0,result.stderr)

    @unittest.skipUnless(os.name=="nt","PowerShell syntax check only on Windows CI")
    def test_probe_has_valid_powershell_syntax_without_running_codex(self):
        pwsh=shutil.which("pwsh") or shutil.which("powershell")
        self.assertIsNotNone(pwsh)
        file=(ROOT/"scripts"/"career-v22-native-skill-probe.ps1").as_posix()
        command=(
            "$e=$null;$tokens=$null;"
            "[System.Management.Automation.Language.Parser]::ParseFile("
            "'"+file+"',[ref]$tokens,[ref]$e)|Out-Null;"
            "if($e.Count -gt 0){$e|Out-String|Write-Error;exit 1}"
        )
        r=subprocess.run([pwsh,"-NoProfile","-NonInteractive","-Command",command],
                         capture_output=True,text=True,timeout=20)
        self.assertEqual(r.returncode,0,r.stderr)

if __name__=="__main__":
    unittest.main()
