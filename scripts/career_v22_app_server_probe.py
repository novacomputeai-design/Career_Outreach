"""Read-only Codex App Server native skill qualification (no private memory).

Uses documented JSONL App Server initialize -> skills/list -> thread/start ->
turn/start with explicit typed skill items. A host-accepted typed skill item
does NOT attest specialist execution. Never uses text or synthetic self-traces
as host invocation proof. All client output is a bounded redacted status.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import queue
import shutil
import subprocess
import sys
import threading
import time

SKILLS = (
    "daily-executive-outreach", "organization-discovery",
    "provenance-and-freshness", "relationship-qualification", "run-quality-audit",
)
PRIVATE_ENV = ("OUTREACH_STATE_KEY", "OUTREACH_IDENTITY_KEY", "OUTREACH_DB_PATH")
MAX_MESSAGES = 3000
MAX_LINE = 1024 * 1024
REQUIRED_MARKER = "career-v22-app-server-skill-qualification"
UNSAFE_ITEMS = {"commandExecution", "fileChange", "mcpToolCall", "dynamicToolCall"}
PROMPT = (
    "Use explicitly injected $daily-executive-outreach and the four supplied "
    "Career Outreach specialist skills ONLY to describe their distinct "
    "responsibilities for a SYNTHETIC, read-only V2.2 qualification. "
    "No tools, commands, web browsing, file reads, file edits, repository "
    "mutations, private memory, DPAPI, relationships, contact details, messages "
    "or applications. Do not assert native execution merely because a skill "
    "was passed to you. If actual specialist execution is not independently "
    "observable, say NOT_VERIFIED. Respond concisely."
)


class QualificationHold(Exception):
    pass


def _same_path(a, b):
    return os.path.normcase(os.path.normpath(str(Path(a).resolve()))) == os.path.normcase(
        os.path.normpath(str(Path(b).resolve()))
    )


def validate_discovery(response, cwd, names=SKILLS):
    """Only trust exact, enabled skill paths returned by the host for this cwd."""
    data = response.get("data")
    if not isinstance(data, list):
        raise QualificationHold("SKILLS_LIST_UNSUPPORTED")
    groups = [g for g in data if isinstance(g, dict)
              and isinstance(g.get("cwd"), str) and _same_path(g["cwd"], cwd)]
    if len(groups) != 1 or groups[0].get("errors"):
        raise QualificationHold("SKILLS_LIST_CWD_OR_ERRORS")
    entries = groups[0].get("skills")
    if not isinstance(entries, list):
        raise QualificationHold("SKILLS_LIST_INVALID")
    found = {}
    for entry in entries:
        if not isinstance(entry, dict) or entry.get("name") not in names:
            continue
        name = entry["name"]
        if name in found:
            raise QualificationHold("DUPLICATE_HOST_SKILL_NAME")
        if entry.get("enabled") is not True:
            raise QualificationHold("DISABLED_REQUIRED_SKILL")
        declared = entry.get("path")
        if not isinstance(declared, str) or not declared:
            raise QualificationHold("HOST_SKILL_PATH_NOT_EXPOSED")
        expected = Path(cwd) / ".agents" / "skills" / name / "SKILL.md"
        if not expected.is_file() or not _same_path(declared, expected):
            raise QualificationHold("HOST_SKILL_PATH_NOT_LOCAL_REPOSITORY")
        found[name] = str(expected.resolve())
    if set(found) != set(names):
        raise QualificationHold("REQUIRED_SKILL_NOT_DISCOVERED")
    return found


class AppServer:
    def __init__(self, command, cwd, timeout=90):
        self.command = list(command)
        self.cwd = str(Path(cwd).resolve())
        self.deadline = time.monotonic() + timeout
        self.events = queue.Queue()
        self.proc = None
        self.next_id = 0
        self.messages = 0
        self.approvals_denied = 0
        self.tool_activity = []
        self.turn_completed = None
        self.completed_turns = {}
        self.notification_names = set()
        self._stopped = False

    def __enter__(self):
        if any(os.environ.get(name) for name in PRIVATE_ENV):
            raise QualificationHold("PRIVATE_OWNER_ENV_PRESENT")
        env = os.environ.copy()
        for name in PRIVATE_ENV:
            env.pop(name, None)
        self.proc = subprocess.Popen(
            self.command, cwd=self.cwd, env=env, shell=False,
            stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL, bufsize=0,
        )
        def read():
            try:
                for raw in self.proc.stdout:
                    if len(raw) > MAX_LINE:
                        self.events.put(QualificationHold("OVERSIZED_HOST_EVENT"))
                        return
                    try:
                        self.events.put(json.loads(raw))
                    except (UnicodeDecodeError, ValueError):
                        self.events.put(QualificationHold("MALFORMED_HOST_JSON"))
                        return
            finally:
                self.events.put(QualificationHold("HOST_CONNECTION_CLOSED"))
        threading.Thread(target=read, daemon=True).start()
        return self

    def __exit__(self, *_):
        if self.proc is not None:
            try:
                self.proc.stdin.close()
            except (OSError, ValueError):
                pass
            if self.proc.poll() is None:
                self.proc.terminate()
                try:
                    self.proc.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    self.proc.kill()
                    self.proc.wait(timeout=3)

    def send(self, payload):
        try:
            self.proc.stdin.write((json.dumps(payload, separators=(",", ":")) + "\n").encode("utf-8"))
            self.proc.stdin.flush()
        except (BrokenPipeError, OSError, ValueError):
            raise QualificationHold("HOST_STDIN_UNAVAILABLE") from None

    def _read(self):
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            raise QualificationHold("APP_SERVER_DEADLINE")
        try:
            msg = self.events.get(timeout=remaining)
        except queue.Empty:
            raise QualificationHold("APP_SERVER_DEADLINE") from None
        if isinstance(msg, Exception):
            raise msg
        if not isinstance(msg, dict):
            raise QualificationHold("HOST_INVALID_EVENT")
        self.messages += 1
        if self.messages > MAX_MESSAGES:
            raise QualificationHold("HOST_EVENT_BUDGET_EXCEEDED")
        if "method" in msg and "id" in msg:
            # Reject every server-initiated request, including approval and
            # dynamic-tool requests. Never accept, auto-review or grant privileges.
            self.approvals_denied += 1
            self.send({"id": msg["id"], "error": {
                "code": -32000, "message": "Read-only qualification declines host requests"}})
            raise QualificationHold("SERVER_REQUEST_OR_APPROVAL_DENIED")
        method = msg.get("method")
        if isinstance(method, str):
            self.notification_names.add(method)
        if method == "turn/completed":
            turn = (msg.get("params") or {}).get("turn") or {}
            if isinstance(turn.get("id"), str):
                self.completed_turns[turn["id"]] = turn.get("status")
        if method in ("item/started", "item/completed"):
            kind = (msg.get("params") or {}).get("item", {}).get("type")
            if kind in UNSAFE_ITEMS:
                self.tool_activity.append(kind)
                raise QualificationHold("UNEXPECTED_TOOL_ACTIVITY")
        return msg

    def request(self, method, params):
        self.next_id += 1
        request_id = self.next_id
        self.send({"id": request_id, "method": method, "params": params})
        while True:
            msg = self._read()
            if msg.get("id") != request_id:
                if "id" in msg:
                    raise QualificationHold("UNEXPECTED_HOST_RESPONSE_ID")
                continue
            if "error" in msg:
                raise QualificationHold("RPC_" + method.replace("/", "_") + "_REJECTED")
            result = msg.get("result")
            if not isinstance(result, dict):
                raise QualificationHold("RPC_RESULT_INVALID")
            return result

    def notify(self, method, params=None):
        self.send({"method": method, "params": params or {}})

    def wait_for_turn(self, expected_id):
        if expected_id in self.completed_turns:
            self.turn_completed = self.completed_turns[expected_id]
            return
        while True:
            msg = self._read()
            if msg.get("method") == "turn/completed":
                turn = (msg.get("params") or {}).get("turn") or {}
                if turn.get("id") != expected_id:
                    raise QualificationHold("TURN_COMPLETION_ID_MISMATCH")
                self.turn_completed = turn.get("status")
                return


def assess_host(cwd, cmd, timeout=90):
    """Attempt host-verified discovery and explicit input; stay HOLD unless proven."""
    repo = Path(cwd).resolve()
    if not (repo / "AGENTS.md").is_file():
        raise QualificationHold("REPOSITORY_NOT_FOUND")
    result = {
        "project_id": "PERSONAL_CAREER_OUTREACH",
        "stage": "APP_SERVER_NATIVE_ACTIVATION",
        "host_skill_discovery": "NOT_VERIFIED",
        "typed_skill_input": "NOT_VERIFIED",
        "host_turn_completed": False,
        "native_specialist_execution": "NOT_VERIFIED",
        "real_research_behavior": "NOT_RUN",
        "private_history_access": "NOT_RUN",
        "outbound_actions": "NOT_AUTHORIZED",
        "status": "HOLD",
        "reason": "UNQUALIFIED",
        "requested_skills": list(SKILLS),
    }
    host = None
    try:
        with AppServer(cmd, repo, timeout=timeout) as host:
            init = host.request("initialize", {"clientInfo": {
                "name": REQUIRED_MARKER, "title": "Career Read-Only Skill Qualification",
                "version": "1.0.0",
            }})
            if not isinstance(init.get("userAgent"), str):
                raise QualificationHold("HOST_INITIALIZATION_UNRECOGNIZED")
            host.notify("initialized")
            discovery = host.request("skills/list", {"cwds": [str(repo)], "forceReload": True})
            paths = validate_discovery(discovery, repo)
            result["host_skill_discovery"] = "PASS_HOST_LISTED_EXACT_PATHS"
            thread = host.request("thread/start", {
                "cwd": str(repo), "approvalPolicy": "never", "sandbox": "read-only",
                "serviceName": REQUIRED_MARKER,
            }).get("thread") or {}
            if not isinstance(thread.get("id"), str) or not thread["id"]:
                raise QualificationHold("THREAD_ID_MISSING")
            inputs = [{"type": "text", "text": PROMPT}] + [
                {"type": "skill", "name": name, "path": paths[name]} for name in SKILLS]
            turn_response = host.request("turn/start", {
                "threadId": thread["id"], "input": inputs,
                "approvalPolicy": "never",
                "sandboxPolicy": {"type": "readOnly", "access": {
                    "type": "restricted", "includePlatformDefaults": True,
                    "readableRoots": [str(repo)],
                }},
            })
            turn = turn_response.get("turn") or {}
            if not isinstance(turn.get("id"), str) or not turn["id"]:
                raise QualificationHold("TURN_ID_MISSING")
            result["typed_skill_input"] = "HOST_ACCEPTED_EXPLICIT_SKILL_ITEMS"
            host.wait_for_turn(turn["id"])
            if host.turn_completed != "completed":
                raise QualificationHold("TURN_NOT_COMPLETED")
            result["host_turn_completed"] = True
            result["reason"] = "HOST_DISCOVERY_AND_EXPLICIT_INPUT_ACCEPTED_NOT_EXECUTION_ATTESTATION"
            # App Server typed skill injection is stronger than a model claim,
            # but does not prove an individual specialist executed. A trusted
            # invocation event could be added by a host-supported telemetry
            # observer; this client does not invent one.
    except (QualificationHold, OSError, ValueError) as exc:
        result["reason"] = str(exc) if isinstance(exc, QualificationHold) else "HOST_PROCESS_ERROR"
    finally:
        if host is not None:
            result["approval_requests_denied"] = host.approvals_denied
            result["unexpected_tool_items"] = sorted(set(host.tool_activity))
            result["host_event_types"] = sorted(host.notification_names)
    return result


def main():
    parser = argparse.ArgumentParser(description="Host-native skill input probe; never production approval")
    parser.add_argument("--repo", required=True)
    parser.add_argument("--codex-bin", required=True)
    parser.add_argument("--codex-entry", help="JS entry when bin is node.exe")
    parser.add_argument("--timeout", type=int, default=90)
    args = parser.parse_args()
    repo = Path(args.repo).resolve()
    if args.timeout < 5 or args.timeout > 180:
        raise SystemExit("Timeout must be 5-180 seconds")
    if any(os.environ.get(k) for k in PRIVATE_ENV):
        raise SystemExit("BLOCKED: protected owner credentials in environment")
    if shutil.which("git") is None:
        raise SystemExit("BLOCKED: git executable unavailable")
    initial = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                             capture_output=True, text=True, timeout=10)
    if initial.returncode or initial.stdout.strip():
        raise SystemExit("BLOCKED: git checkout not clean")
    if args.codex_entry:
        argv = [args.codex_bin, args.codex_entry]
    else:
        argv = [args.codex_bin]
    argv += ["-c", "mcp_servers.notion.enabled=false", "app-server"]
    report = assess_host(repo, argv, timeout=args.timeout)
    final = subprocess.run(["git", "-C", str(repo), "status", "--porcelain"],
                           capture_output=True, text=True, timeout=10)
    if final.returncode or final.stdout.strip():
        report["reason"] = "WORKING_TREE_CHANGED_DURING_HOST_DIAGNOSTIC"
        report["status"] = "HOLD"
    print(json.dumps(report, indent=2))
    # HOLD is an observed outcome, not a process crash. Unsafe/malformed
    # protocol still fails closed; no process here grants permission.


if __name__ == "__main__":
    main()
