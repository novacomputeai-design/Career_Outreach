# Career V2.2 App Server Native Skill Handoff — DRAFT

Status: engineering candidate, NOT live-host verified and NOT production. This is the final targeted native-skill activation remediation.

## Supported protocol

Based on the official Codex App Server protocol: JSONL stdio, initialize then initialized, skills/list with cwds and forceReload, thread/start, and turn/start with typed skill items containing type, name, path alongside explicit skill-name text. The adapter uses these supported host API calls rather than asserting activation from a model response.

The adapter in scripts/career_v22_app_server_probe.py:
1. Launches a temporary Codex App Server, with the unrelated Notion MCP disabled for this invocation only.
2. Rejects owner private credentials in its environment and requires a clean Git working tree.
3. Calls skills/list with the actual repository cwd. It requires exact enabled paths for the orchestrator plus organization-discovery, provenance-and-freshness, relationship-qualification and run-quality-audit. Missing paths, duplicate names, disabled or missing skills and incompatible API return HOLD without fallback.
4. Requests approvalPolicy=never and a restricted read-only sandbox; sends explicit typed skill inputs only after host discovery.
5. Declines all server-initiated requests. Unexpected command, file-change, MCP or dynamic-tool execution, timeouts and malformed events produce HOLD.
6. Prints a privacy-minimized summary only. No raw model text or private history is saved by the adapter.

## Evidence boundaries

- Repository skill file presence or model assertions: NOT native activation evidence.
- Host skills/list enabled exact paths: PASS_HOST_LISTED_EXACT_PATHS.
- Host acknowledges turn/start including typed skill items: HOST_ACCEPTED_EXPLICIT_SKILL_ITEMS; host input accepted, not evidence specialists actually executed.
- Completed host turn: proves only a turn completed.
- Actual specialist execution requires separately trustworthy host skill-invocation telemetry and observed behavior.
- With no authoritative execution event, native_specialist_execution remains NOT_VERIFIED, and overall status remains HOLD.

This adapter never promotes host input acceptance into native specialist execution qualification. Fake-server protocol tests are tests of the client, not of the user's Codex host.

## Operator run

From a normal owner PowerShell shell, after a fast-forward pull on feat/career-intelligence-v2-2-e2e-hardening, run:

    .\scripts\career-v22-app-server.ps1

The wrapper uses codex.cmd when available and otherwise the validated local Node package entry on nvm installations. Share the summary JSON fields, not any raw host logs. Do not run it inside an AI agent or a session with private relationship keys. The tool may leave its own Codex thread data outside Git; it does not touch the user-owned private database.

A restricted read-only Codex policy is not OS-level isolation and cannot establish that the host can never read any user resources. The only supported claim is that this client declines approvals and tool requests and flags unexpected tool activity. This is never contact authorization.

## Mandatory fallback rather than more self-certification

If the local host cannot expose skills/list paths, rejects typed skill items, or provides no credible execution attestation:
1. Record the exact HOLD reason.
2. Stop repeating native-activation prompts.
3. Continue with observable behavioral tests using scripts/career-v22-synthetic-only.ps1, the 54 named adversarial scenarios, and independent owner-reviewed source, memory and recovery checks; mark unexecuted cases NOT_RUN.
4. Keep the production release decision NO-GO pending the actual P4/P5 gate and human relevance evaluation.

No sending, applications, DPAPI access, policy override or repository merge is authorized.

References:
https://learn.chatgpt.com/docs/app-server
https://openai.com/index/unlocking-the-codex-harness/
