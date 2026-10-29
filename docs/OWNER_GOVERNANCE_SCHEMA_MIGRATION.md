# Explicit owner-approved governance schema migration

**Status: COMPLETE — owner-verified LIVE migration on 2026-10-28.** The authorized owner ran the backup-first migration in ordinary Windows PowerShell outside Codex. The original records were reported unchanged. This is owner-terminal evidence, not a GitHub-hosted private database inspection.

The original private SQLite database was created before the `governance_decisions` table. Same-account encrypted backup/restore and the additive migration on a recovered COPY passed, followed by the distinct owner-authorized LIVE migration. There is no need to rerun it on the current database.

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

**P0 outcome:** The hardened store rejects implicit legacy migrations and verifies every existing person's digest. The distinct live owner decision was granted and migration completed. Do not execute migrations from Codex.

**P0 hardening:** Regular writable opens of an unmigrated legacy database fail closed; the original identity HMAC key must match existing people before any read/write. This safeguard still applies to any restored legacy copy.

## Live migration completion record

On 2026-10-28 the owner ran the guarded command on `%LOCALAPPDATA%\CareerOutreach\relationships.sqlite`. Terminal output included `AUTHENTICATED_SQLITE_BACKUP_VALID` for its pre-change legacy snapshot, `original_keys_match=true`, then `LIVE GOVERNANCE MIGRATION VERIFIED`, `Pre-change encrypted backup: VERIFIED`, `Existing relationship record counts: UNCHANGED`, `Governance audit schema: CURRENT`, `No outreach authorized or sent.` The earlier owner inspection had 2 people, 2 events and 1 preference. The pre-change backup's `live_database_modified=false` applies to BACKUP VERIFICATION, not to the deliberately applied migration. Avoid rerunning the migration; a new need for schema changes requires its own authorization.

This tool is not a complete identity, novelty or source verification system. Full contact-ready eligibility and `SEND_AUTHORIZED` remain blocked. The secure off-device recovery of both original keys remains unqualified.
