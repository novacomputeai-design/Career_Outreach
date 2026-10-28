# Explicit owner-approved governance schema migration

**Status:** code and synthetic qualification only. Existing private relationship memory is not modified by GitHub changes. This migration must run under the owner's ordinary Windows account **outside Codex** and must be authorized separately.

The original private SQLite database was created before the `governance_decisions` table. Its relationship records are valid and have already passed owner-Windows encrypted backup, authenticated verification and restore-new qualification. The newer governance audit commands require that table; an owner-approved additive migration is needed.

## Safe migration contract

- `inspect` opens only a read-only existing SQLite file and returns the recognized schema and aggregate counts; it does not open DPAPI keys or modify the database.
- `migrate` requires explicit `-IApproveSchemaChange`. It verifies original DPAPI-protected Fernet and HMAC keys, makes a new consistent **encrypted** pre-change backup, verifies that backup with both keys, then uses one SQLite transaction to add only the missing governance decision table and an encrypted, versioned system migration audit event. It rejects missing base tables, changed data counts, missing keys and invalid backups.
- A current schema returns `ALREADY_CURRENT_NO_CHANGES`; migration is never repeated.
- Contact identities, relationship states, preferences, outreach history, suppression and draft state are not rewritten; no sender exists. No private records or plaintext keys go to Git.

## First test on the existing recovery COPY

Run in ordinary PowerShell, not from Codex. **Do not test the live file first.** After CI has passed and the change is merged:

```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
git pull --ff-only

$folder = Join-Path $env:LOCALAPPDATA "CareerOutreach\backups"
$testCopy = Get-ChildItem -LiteralPath $folder -Filter "recovery-proof-*.sqlite" -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 -ExpandProperty FullName

if (-not $testCopy) { throw "Recovery test copy not found. Stop." }

pwsh -NoProfile -File .\scripts\owner-memory-schema.ps1 -Mode inspect -Database $testCopy
```

If you explicitly choose to test adding the audit table to this **recovered test copy only**:

```powershell
pwsh -NoProfile -File .\scripts\owner-memory-schema.ps1 -Mode migrate -Database $testCopy -IApproveSchemaChange
if ($LASTEXITCODE -ne 0) { throw "Test-copy migration failed. Stop." }
pwsh -NoProfile -File .\scripts\owner-memory-schema.ps1 -Mode inspect -Database $testCopy
```

Expected `GOVERNANCE_AUDIT_SCHEMA_ADDED`, `backup_verified_before_change=true`, `original_relationship_row_counts_unchanged=true`, and `CURRENT_WITH_GOVERNANCE_AUDIT` for the **test copy**. The live file remains untouched. Do not share private SQLite or snapshot files in chat.

**P0 prerequisite:** The hardened store rejects implicit legacy migrations and verifies every existing record's identity digest against the original HMAC key. The live database still requires a distinct owner decision after qualification. Do not run on the live file from Codex.

## Live migration remains separate

After independent test-copy qualification, the operator may explicitly choose to migrate the **live** `%LOCALAPPDATA%\CareerOutreach\relationships.sqlite` via the same owner tool with `-Database` set to that exact live file and `-IApproveSchemaChange`. This requires a specific operator decision. Do not automate the live migration or allow Codex to invoke it.

This tool is not a complete identity, novelty or source verification system. Full contact-ready eligibility and `SEND_AUTHORIZED` remain blocked. The secure off-device recovery of both original keys remains unqualified.
