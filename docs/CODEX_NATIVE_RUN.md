# Codex-primary Career Outreach activation

Architecture chosen October 27, 2026: **Codex CLI is the agent**, and all 14 local `.agents/skills/` packages are its procedures. Python is the deterministic check and private memory helper. The older `python -m outreach_agent run` uses Tavily and OpenAI API keys and is **optional, not the chosen Codex path**.

User-reported Windows diagnostic: `codex-cli 0.164.0`, logged in using ChatGPT. Offline tests: 41 passed. Protected local SQLite initialized and settings persisted. **Native skill loading is not yet proven.**

## First proof — read only

In PowerShell:

```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
git pull --ff-only
codex
```

Within interactive Codex, select the available native skill named `$daily-executive-outreach` (use the host skill picker if available) and submit:

> Use the native $daily-executive-outreach skill for a READ-ONLY activation test. Do not research actual people yet, create or change files, contact anyone, or access private records. Report whether the host discovered this skill in its native skill catalog, how it was selected, the skill file you loaded, other available Career Outreach skills, and any missing activation evidence. Reading a SKILL.md file directly without supported skill selection is NOT VERIFIED. Do not claim live browsing or contact readiness.

Capture a redacted execution transcript showing the actual selection mechanism and invoked procedure. Skill directory presence, Codex login, and passing offline tests are insufficient alone.

## After native activation is proven

With explicit permission, run a small supervised five-person public-source research trial; require credible fresh source evidence, legitimate individual contact routes, private identity-history review, and no messages sent. If permitted live browsing is unavailable, stop and report the gap rather than silently switching to another API.

No private contact history or credentials should be stored in Git. The protected SQLite path is outside the checkout. The current Python CLI does not yet implement a full Codex-compatible candidate ingestion and novelty verification interface, so confirmed new contact-ready counts must remain zero until that bridge and review process are verified.

Only after the live pilot, seven real daily runs and independent review should we evaluate unattended Codex execution. Current scheduler examples invoke the OPTIONAL older Python provider runtime, not Codex.
