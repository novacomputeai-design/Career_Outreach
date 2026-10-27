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

No private contact history or credentials should be stored in Git. The protected SQLite path is outside the checkout. The Python CLI has a user-reported relationship capture and a read-minimized relationship lookup (see next section). These do NOT constitute complete provenance-verified candidate ingestion, independent human review, or cross-channel novelty verification. Confirmed new contact-ready counts must remain zero until those additional gates are verified.

Only after the live pilot, seven real daily runs and independent review should we evaluate unattended Codex execution. Current scheduler examples invoke the OPTIONAL older Python provider runtime, not Codex.

## User-declared relationship capture — protected local workflow

After pulling the merged feature, run in PowerShell with the existing encrypted database and DPAPI-protected key files available in your Windows user profile. **Keep credentials out of prompts and Git.** These interactive commands deliberately request names privately rather than putting relationships in PowerShell history.

```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$env:OUTREACH_DB_PATH = Join-Path $private "relationships.sqlite"
$env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new(
    "", ((Get-Content (Join-Path $private "state-key.dpapi") -Raw).Trim() | ConvertTo-SecureString)
).Password
$env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new(
    "", ((Get-Content (Join-Path $private "identity-key.dpapi") -Raw).Trim() | ConvertTo-SecureString)
).Password

# Interactive: enter a full name, FIRST_LEARNED or PREVIOUSLY_MET, optional individual official profile URL.
.\.venv\Scripts\python.exe -m outreach_agent remember-relationship

# Repeat for the second person.
.\.venv\Scripts\python.exe -m outreach_agent remember-relationship

# Read-minimized checks can be executed for an exact public name by the operator.
.\.venv\Scripts\python.exe -m outreach_agent relationship-check --person-name "Example Person"

# Clear the credentials from the current PowerShell process once finished.
Remove-Item Env:OUTREACH_STATE_KEY, Env:OUTREACH_IDENTITY_KEY, Env:OUTREACH_DB_PATH -ErrorAction SilentlyContinue
```

Use exact public full names (no Dr./Mr. prefix). Do not enter a general organizational contact page as an individual profile. Classifications are `FIRST_LEARNED` (user says this is the first time they learned of the person; no previous contact known to them) or `PREVIOUSLY_MET` (existing relationship). They are user-reported facts, not independently verified sourcing or hiring interest.

A lookup returns only a coarse classification/hold reason; unknown does **NOT** equal objectively new. Conflicting names/profiles or suppression fail closed. No event is fabricated, no drafting is approved, and sending remains disabled. This first manual bridge is not yet a fully validated Codex agent execution across the private store. Native specialist activation and end-to-end privacy tests remain separate.
