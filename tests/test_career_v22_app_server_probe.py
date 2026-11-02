"""Fake App Server protocol tests: no real Codex, no network or private memory."""
from pathlib import Path
import json
import os
import subprocess
import sys
import tempfile
import unittest

from scripts.career_v22_app_server_probe import (
    SKILLS, assess_host, validate_discovery, QualificationHold,
)

FAKE = r'''
import json,sys
from pathlib import Path
case=sys.argv[1]
def emit(value):
    print(json.dumps(value),flush=True)
for line in sys.stdin:
    req=json.loads(line)
    method=req.get("method")
    if method=="initialized": continue
    ident=req.get("id")
    if method=="initialize":
        emit({"id":ident,"result":{"userAgent":"mock-test/0.1"}})
    elif method=="skills/list":
        cwd=req["params"]["cwds"][0]
        names=("daily-executive-outreach","organization-discovery","provenance-and-freshness",
               "relationship-qualification","run-quality-audit")
        skills=[]
        for n in names:
            path=str(Path(cwd)/".agents"/"skills"/n/"SKILL.md")
            if case=="bad_path" and n=="organization-discovery":
                path=str(Path(cwd)/"not-trusted"/"SKILL.md")
            row={"name":n,"path":path,"enabled":True}
            if case=="missing_path" and n=="run-quality-audit": del row["path"]
            skills.append(row)
        if case=="missing_skill": skills=skills[:-1]
        if case=="duplicate_skill": skills.append(skills[0])
        if case=="disabled_skill": skills[2]["enabled"]=False
        emit({"id":ident,"result":{"data":[{"cwd":cwd,"skills":skills,"errors":[]}]}})
    elif method=="thread/start":
        assert req["params"]["sandbox"]=="read-only"
        assert req["params"]["approvalPolicy"]=="never"
        emit({"id":ident,"result":{"thread":{"id":"test-thread"}}})
    elif method=="turn/start":
        inputs=req["params"]["input"]
        skills=[x for x in inputs if x.get("type")=="skill"]
        assert [x["name"] for x in skills]==[
            "daily-executive-outreach","organization-discovery",
            "provenance-and-freshness","relationship-qualification",
            "run-quality-audit"]
        assert req["params"]["sandboxPolicy"]["type"]=="readOnly"
        access=req["params"]["sandboxPolicy"]["access"]
        assert access["type"]=="restricted"
        assert access["includePlatformDefaults"] is True
        assert access["readableRoots"]==[req["params"]["cwd"]] if "cwd" in req["params"] else len(access["readableRoots"])==1
        if case=="reject_turn":
            emit({"id":ident,"error":{"code":-32600,"message":"unsupported skill input"}})
        else:
            if case=="early_complete":
                emit({"method":"turn/completed","params":{"turn":{"id":"turn-one","status":"completed"}}})
            emit({"id":ident,"result":{"turn":{"id":"turn-one","status":"inProgress"}}})
            if case=="command":
                emit({"method":"item/started","params":{"item":{"type":"commandExecution"}}})
            elif case=="approval":
                emit({"id":200,"method":"item/commandExecution/requestApproval","params":{"threadId":"test-thread"}})
            elif case!="early_complete":
                emit({"method":"turn/completed","params":{"turn":{
                    "id":"turn-one","status":"failed" if case=="failed_turn" else "completed"
                }}})
'''

def fixture(root):
    (root/"AGENTS.md").write_text("Test-only project with no private data",encoding="utf-8")
    for name in SKILLS:
        p=root/".agents"/"skills"/name/"SKILL.md"
        p.parent.mkdir(parents=True,exist_ok=True)
        p.write_text("Synthetic skill.",encoding="utf-8")


class AppServerSkillProbeTests(unittest.TestCase):
    def _run(self, case):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            fixture(root)
            fake=root/"mock_app_server.py"
            fake.write_text(FAKE,encoding="utf-8")
            cmd=[sys.executable,"-u",str(fake),case]
            return assess_host(root,cmd,timeout=8)

    def test_host_explicitly_accepts_typed_skill_inputs_but_not_execution(self):
        result=self._run("ok")
        self.assertEqual(result["host_skill_discovery"],"PASS_HOST_LISTED_EXACT_PATHS")
        self.assertEqual(result["typed_skill_input"],"HOST_ACCEPTED_EXPLICIT_SKILL_ITEMS")
        self.assertTrue(result["host_turn_completed"])
        self.assertEqual(result["native_specialist_execution"],"NOT_VERIFIED")
        self.assertEqual(result["status"],"HOLD")
        self.assertEqual(result["outbound_actions"],"NOT_AUTHORIZED")
        self.assertEqual(result["approval_requests_denied"],0)

    def test_early_turn_completion_not_lost_before_rpc_response(self):
        result=self._run("early_complete")
        self.assertTrue(result["host_turn_completed"])

    def test_absent_skills_and_paths_fail_closed(self):
        for case in ("missing_skill","missing_path","bad_path","duplicate_skill","disabled_skill"):
            with self.subTest(case=case):
                r=self._run(case)
                self.assertEqual(r["status"],"HOLD")
                self.assertEqual(r["typed_skill_input"],"NOT_VERIFIED")

    def test_rejected_skill_rpc_is_hold(self):
        result=self._run("reject_turn")
        self.assertIn("RPC_turn_start_REJECTED",result["reason"])
        self.assertFalse(result["host_turn_completed"])

    def test_failed_turn_is_hold(self):
        result=self._run("failed_turn")
        self.assertEqual(result["reason"],"TURN_NOT_COMPLETED")

    def test_tool_activity_and_approval_are_not_auto_authorized(self):
        cmd=self._run("command")
        self.assertEqual(cmd["reason"],"UNEXPECTED_TOOL_ACTIVITY")
        self.assertIn("commandExecution",cmd["unexpected_tool_items"])
        approval=self._run("approval")
        self.assertEqual(approval["reason"],"SERVER_REQUEST_OR_APPROVAL_DENIED")
        self.assertEqual(approval["approval_requests_denied"],1)

    def test_untrusted_external_path_cannot_be_accepted(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            fixture(root)
            payload={"data":[{"cwd":str(root),"errors":[],"skills":[
                {"name":n,"enabled":True,
                 "path":str(root/".agents"/"skills"/n/"SKILL.md")}
                for n in SKILLS]}]}
            payload["data"][0]["skills"][0]["path"]=str(root/"elsewhere"/"SKILL.md")
            with self.assertRaises(QualificationHold):
                validate_discovery(payload,root)

if __name__=="__main__":
    unittest.main()
