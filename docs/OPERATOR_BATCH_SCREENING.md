# Operator-only protected batch relationship screening

**Status: operator Windows DPAPI batch screening PASSED (prior three-name proof).** The new minimal reconciliation/ordered batch binding is implemented with synthetic tests but requires a separate real Windows owner check. Automatic Codex-to-DPAPI access remains BLOCKED.
This is the first P2 bridge in [Production Plan](PRODUCTION_PLAN.md). It does NOT let Codex decrypt the private database, send messages, authorize drafts, or independently prove a contact new across all prior communication channels.

## Boundary

- **Run in normal trusted Windows PowerShell outside Codex.** The authenticated Codex sandbox failed to decrypt CurrentUser DPAPI-protected keys in a real attempt; do not bypass sandbox or re-create keys.
- The local `%LOCALAPPDATA%\CareerOutreach\candidate-batch.json` contains only the public names (and optional public individual profile URLs) to screen. It MUST NOT be committed to Git.
- Wrapper `scripts/relationship-batch-check.ps1` loads existing DPAPI files in a short-lived operator-side process, runs Python with SQLite read-only mode, clears child environment variables, and prints only minimal per-name classifications.
- Codex should receive classifications **only when the operator explicitly chooses to provide them**, labeled OPERATOR-PROVIDED. Missing local match is still **UNVERIFIED** rather than NEW. Profile collisions remain held.

## Windows operator proof

With the latest Git checkout and existing encrypted private database, in an ordinary **non-Codex** PowerShell terminal:

```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
git pull --ff-only

$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$inputFile = Join-Path $private "candidate-batch.json"

# Synthetic diagnostic names; do not commit this private file.
@("Synthetic Leader", "Another Synthetic") |
  ConvertTo-Json |
  Set-Content -LiteralPath $inputFile -Encoding utf8

pwsh -NoProfile -File .\scripts\relationship-batch-check.ps1
```

On some Python versions/Windows PowerShell variants, JSON UTF-8 BOM handling can differ. If the script fails due to a BOM, save the JSON with `[System.IO.File]::WriteAllText($inputFile, (ConvertTo-Json @("Synthetic Leader","Another Synthetic")), [System.Text.UTF8Encoding]::new($false))` and repeat. This test uses deliberately fictional names and does not change contact history.

Expected `verification_level`: `OPERATOR_PROTECTED_LOCAL_STORE_ONLY`. A SHA-256 `input_fingerprint` of the ordered public names and optional profile URLs now accompanies the result; this prevents accidental batch mixups but does NOT authenticate the operator. Expected `new_contact_ready_granted`: `0`. Unknown fictional people should be `NOT_FOUND_IN_LOCAL_STORE` with `novelty: UNVERIFIED`.

After the synthetic test passes, the operator may replace the batch JSON with actual **previously researched public executive names** from a Codex-generated report. Limit 1–100 entries; each entry may be a name string or `{"person_name": "...", "profile_url": "https://..."}`. Input file must stay under private `%LOCALAPPDATA%\CareerOutreach`.

## Output semantics

- `EXISTING_RELATIONSHIP` / `PREVIOUSLY_MET` → follow-up, not a new discovery.
- `SEEN_IN_STORE` / `FIRST_LEARNED` → already discovered, may still be eligible for first outreach after independent source/route review. Do not count as a NEW discovery in later runs.
- `NOT_FOUND_IN_LOCAL_STORE` → **UNVERIFIED** cross-channel novelty, never auto-count as NEW.
- `DUPLICATE_IN_BATCH_HOLD`, identity conflict or suppressed → hold/remove from new prospect consideration.
- Independent human source/contact-route review plus runtime governance must still pass; the batch checker never grants CONTACT_READY or sending permission.

## Outstanding qualification

This operator-only method is a **manual transfer**, not automatic secure agent integration. Required follow-on: independent user Windows proof, input validation and failure drill, protected backup/restore test, trusted batch output-to-Codex handoff with minimization and consent, deterministic policy decision/audit trail, and eventually a narrow trusted host-side broker only if unattended access is necessary.

Never run the wrapper inside the Codex sandbox, upload private records to GitHub or weaken user-account DPAPI protection.

## Minimal operator reconciliation handoff (new; owner field qualification pending)

After Codex produces **public research names only**, the owner places a private JSON list of candidate records under `%LOCALAPPDATA%\CareerOutreach` (each with `project_id: PERSONAL_CAREER_OUTREACH`, `person_name`, optional `profile_url` and the publicly sourced `why_connect`). In the same exact order, prepare `candidate-batch.json` with only names/profile URLs. Do not give Codex private notes or keys.

In ordinary trusted PowerShell **outside Codex**, run:

```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
$private = Join-Path $env:LOCALAPPDATA 'CareerOutreach'
$batch = Join-Path $private 'candidate-batch.json'
$publicNames = Join-Path $private 'candidate-public-review.json'
$screenResult = Join-Path $private 'screening-result.json'
$reviewResult = Join-Path $private 'operator-review-report.json'
# Candidate and batch files must already exist in the SAME order with matching names/profiles.
# The screen-result output should not overwrite an existing file from a different run.
if (Test-Path $screenResult) { throw 'Choose a fresh screening-result path to avoid mixing runs' }
pwsh -NoProfile -File .\scripts\relationship-batch-check.ps1 -InputFile $batch |
    Set-Content -LiteralPath $screenResult -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw 'Protected batch screening failed' }
.\.venv\Scripts\python.exe .\scripts\reconcile_operator_screening.py `
    --candidates $publicNames --screening $screenResult --output $reviewResult
if ($LASTEXITCODE -ne 0) { throw 'Reconciliation failed; no novelty clearance' }
```

The new report is strictly an owner-local classification queue. **Every candidate remains `contact_ready=false`; `NOT_FOUND_IN_LOCAL_STORE` remains `NOVELTY_UNVERIFIED_HOLD`.** Profile changes, swapped names/batches, misrepresented novelty, missing or suppressed records and Nova-sales intent HOLD. The SHA fingerprint is not a digital signature and does not grant trusted Codex integration. The owner decides whether to supply any minimal classification to Codex, and never exposes private memory records, keys, notes or encrypted files. Use a new private filename per run and never commit it.
