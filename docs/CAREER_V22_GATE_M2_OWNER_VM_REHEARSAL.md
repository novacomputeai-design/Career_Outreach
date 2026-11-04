# Gate M2 — disposable Windows owner-only qualification (DRAFT / NOT YET EXECUTED)

**Goal:** Exercise protected memory, independently fetched public-text receipts,
owner review, journal integrity and negative controls in a disposable Windows
guest using ONLY synthetic people and randomly generated guest-only keys.

**This document is an OWNER-RUN procedure, not a Codex action.** Never execute
owner-career-v22.ps1, owner-memory-backup.ps1, or this bootstrap through Codex.
Do not run it in the user's existing Windows profile, against the production
CareerOutreach folder, or from a scheduled task. Creating and operating the VM
is a manual owner action and is not attested by the GitHub CI tests.

## Prerequisites and hard isolation

1. Create a **new disposable Windows VM** (Hyper-V, VMware, VirtualBox, etc.),
   an unrelated test Windows user, and a guest snapshot. Do not share the host's
   user profile, AppData, personal files, keys or backup folders into this VM.
   Do not sign into personal email, browser profiles or connected accounts.
2. From **inside the VM**, clone
   `novacomputeai-design/Career_Outreach` at
   `feat/career-v22-contribution-evidence-hardening`; verify and record
   `git rev-parse HEAD`. The PR remains draft; do not merge.
3. Inside the VM only, use normal interactive PowerShell:
   ```powershell
   cd C:\Career-Outreach-M2-Guest
   python -m venv .venv
   .\.venv\Scripts\python.exe -m pip install -r requirements.txt
   Get-CimInstance Win32_ComputerSystem | Select-Object Manufacturer,Model
   Test-Path (Join-Path $env:LOCALAPPDATA "CareerOutreach")
   ```
   The last command **MUST be False**. If True, stop and discard this VM.
   Guest model must be recognized as virtual. Do not bypass the check.
4. Only **after confirming this is the guest**, create the manual marker:
   ```powershell
   New-Item -ItemType File -Path (Join-Path $env:SystemDrive "CAREER_M2_DISPOSABLE_GUEST.marker") -ErrorAction Stop
   pwsh -NoProfile -File .\scripts\gate-m2-disposable-guest-seed.ps1 -ConfirmDisposableGuest
   ```
   Type the exact confirmation phrase when prompted. The guarded seeder rejects
   an existing private folder, creates test-only random Fernet/HMAC keys and
   protects them with the guest user's Windows DPAPI. It creates three synthetic
   stored people and four synthetic research opportunities outside Git.
   It does NOT import data from the host. There is no override to reuse an
   existing private folder.

**IMPORTANT:** VM-model and marker checks are guardrails, not cryptographic
proof of guest isolation. The owner must verify the VM and host-sharing
configuration independently. If that cannot be established, stop at HOLD.

## A. Encrypted backup, verify, restored-copy identities (item 2)

Inside the guest, in the repo worktree:

```powershell
pwsh -NoProfile -File .\scripts\owner-memory-backup.ps1 -Mode backup
if ($LASTEXITCODE -ne 0) { throw "M2_BACKUP_FAILED" }

$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$backupDir = Join-Path $private "backups"
$snapshot = Get-ChildItem $backupDir -Filter '*.fernet' -File |
  Sort-Object LastWriteTime -Descending | Select-Object -First 1 -ExpandProperty FullName
if (-not $snapshot) { throw "M2_SNAPSHOT_MISSING" }

pwsh -NoProfile -File .\scripts\owner-memory-backup.ps1 -Mode verify -Snapshot $snapshot
if ($LASTEXITCODE -ne 0) { throw "M2_SNAPSHOT_VERIFY_FAILED" }

$restored = Join-Path $backupDir ("m2-restored-" + [guid]::NewGuid().ToString("N") + ".sqlite")
pwsh -NoProfile -File .\scripts\owner-memory-backup.ps1 -Mode restore-new -Snapshot $snapshot -Destination $restored
if ($LASTEXITCODE -ne 0) { throw "M2_RESTORE_FAILED" }

pwsh -NoProfile -File .\scripts\gate-m2-disposable-guest-verify.ps1 -RestoredDb $restored
if ($LASTEXITCODE -ne 0) { throw "M2_RESTORED_IDENTITIES_FAILED" }
```

Require: `ENCRYPTED_SNAPSHOT_CREATED`,
`AUTHENTICATED_SQLITE_BACKUP_VALID`, `RESTORED_TO_NEW_PRIVATE_PATH`,
and `restored_memory_verified=true`. The verifier opens only the restored
file in read-only mode and checks: Pat Example = PREVIOUSLY_MET,
a different Pat profile = POSSIBLE_NAMESAKE_HOLD, Alex Example =
SEEN_IN_STORE, and Jordan Example = SUPPRESSED. All contact authority false.

## B. Bounded source-text witness and exact packet binding (item 3)

The fixture's ONLY source is `https://example.com/`; every synthetic
claim uses the public phrase "Example Domain". This is an intentional
**semantic mismatch**: reproducing text is not verifying real employer
initiatives, role ownership, timing, or hiring. Treat any such claim as fake.

```powershell
$packet = Join-Path $private "runs\m2-synthetic-packet.json"
$report = Join-Path $private "runs\m2-synthetic-report.json"
$witness = Join-Path $private ("runs\m2-witness-" + [guid]::NewGuid().ToString("N") + ".json")

pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode SourceWitness -Packet $packet -Out $witness -AllowHost example.com
if ($LASTEXITCODE -ne 0) { throw "M2_SOURCE_WITNESS_FAILED" }
```

The FETCH challenge is interactive. Verify that receipt claim IDs and URL
coverage match the packet, and that `semantic_claims_verified=false`,
`source_truth_independently_verified=false`,
`contact_ready=false`, and `send_authorized=false`. If DNS pinning,
TLS, HTTP status or network isolation prevents fetching, record
`FETCH_UNAVAILABLE`/HOLD. **Never** relax host allowlists, TLS checks,
IP filtering or redirect restrictions to force a pass.

Create a **new copy** of the witness and change `packet_sha256` in that
copy without recomputing the HMAC. Use the copied receipt with OwnerReview:
the owner CLI must reject it before any decision is appended, with
`SOURCE_WITNESS_BINDING_INVALID`. Never edit the original receipt.

## C. Owner-review challenges, relationship identity, opt-outs (item 4)

Use the **unmodified** report and witness. The fixture contains these
four distinct opportunity indices and public-profile inputs:

| Index | Synthetic identity | Profile to enter | Expected local result |
|---|---|---|---|
| 0 | Pat Example | https://example.org/professional/pat-one | EXISTING_RELATIONSHIP |
| 1 | Pat Example | https://example.org/professional/pat-other | POSSIBLE_NAMESAKE_HOLD |
| 2 | Jordan Example | https://example.org/professional/jordan | EXISTING_RELATIONSHIP, suppressed=true |
| 3 | Alex Example | https://example.org/professional/alex | SEEN_IN_STORE |

Use this owner-only command, adjusting `-Index`:

```powershell
pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode OwnerReview -Report $report -Witness $witness -Index 0 -Decision RESEARCH_MORE -Reason SOURCE_GAP
```

First, deliberately type a **wrong** `REVIEW <hash>` challenge; it must
reject the decision and leave zero journal events. Use
`-Mode VerifyJournal` to confirm zero. Then repeat with the exact
challenge for index 0, and perform research-only RESEARCH_MORE reviews
for indices 1, 2 and 3. Check the local classifications printed and
record `verified_events=4` after all accepted decisions.

For index 2, additionally try `-Decision PURSUE -Reason LEADERSHIP_SCOPE`
with the correct challenge *before* the RESEARCH_MORE review; it must
fail due to suppression and append nothing. The owner review does not
grant messaging, scheduling or application authority. Never enter a real
contact profile or address in this rehearsal.

## D. Journal integrity and tampering (item 5)

```powershell
pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode VerifyJournal
if ($LASTEXITCODE -ne 0) { throw "M2_ORIGINAL_JOURNAL_NOT_VERIFIED" }

Copy-Item -LiteralPath (Join-Path $private "owner-v22") -Destination (Join-Path $private "owner-v22-tampered-copy") -Recurse -ErrorAction Stop
$copy = Join-Path $private "owner-v22-tampered-copy"
$file = Join-Path $copy "owner-reviews.jsonl"
$originalText = [IO.File]::ReadAllText($file)
if (-not $originalText.Contains("SOURCE_GAP")) { throw "M2_EXPECTED_TEST_EVENT_MISSING" }
[IO.File]::WriteAllText($file, $originalText.Replace("SOURCE_GAP","ROLE_MATCH"))
pwsh -NoProfile -File .\scripts\gate-m2-disposable-guest-verify.ps1 -TamperedJournalCopy $copy
if ($LASTEXITCODE -ne 0) { throw "M2_TAMPER_REJECTION_NOT_CONFIRMED" }
```

Expected: `M2_TAMPERED_JOURNAL_INTEGRITY_REJECTED`, and the intact
owner-v22 journal still passes independently with four events. Do not
modify the original journal or use `-Force` to overwrite private files.

## M2 evidence and sign-off

Record in a **private file outside Git**: VM type and disposable guest
identity (no personal account details), exact candidate SHA, time,
Windows/Python versions, snapshot/restore statuses, exact witness
summary, four classifications, negative challenge outcome, suppressed
PURSUE rejection, journal event count and copied-journal rejection.
Do NOT export unredacted keys, DPAPI files, private SQLite data, or raw
personal relationship records.

- **PASS_OWNER_WINDOWS_ISOLATED:** Every owner-only step actually ran
  in a disposable guest; proof shows no host data was mounted/read.
- **HOLD:** Any VM, key, source fetch, identity classification, receipt
  binding, protected backup, journal, or challenge behavior not witnessed.
- **FAIL:** Any unapproved contact/send/application state, live-data access,
  modified original memory, accepted tampered receipt, or accepted tampered
  journal; stop, preserve non-sensitive diagnostics and discard VM.

The parallel GitHub synthetic unit tests **cannot** award this gate.
Native host activation remains NOT_VERIFIED; M3 source-semantic checks
and M4 supervised field benchmark remain subsequent separate gates.
Do not merge PR #27, modify main, or activate production based on M2.
