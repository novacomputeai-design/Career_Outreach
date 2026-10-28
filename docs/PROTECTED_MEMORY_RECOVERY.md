# Protected memory recovery (owner-only)

This feature snapshots the SQLite relationship database consistently in memory, encrypts the result with the existing local state key, and checks the original identity key when verifying. It NEVER replaces the live database and never sends messages.

**Run ONLY in your own ordinary PowerShell session, outside Codex.** No DPAPI decryption from inside the Codex sandbox. Both original keys are required, and the generated encrypted snapshot alone is not portable across Windows accounts. Real Windows verification is still pending.

## Windows test (after merging)

```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
git pull --ff-only
pwsh -NoProfile -File .\scripts\owner-memory-backup.ps1 -Mode backup
$dir = Join-Path $env:LOCALAPPDATA "CareerOutreach\backups"
$snapshot = Get-ChildItem -LiteralPath $dir -Filter '*.fernet' -File |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1 -ExpandProperty FullName
pwsh -NoProfile -File .\scripts\owner-memory-backup.ps1 -Mode verify -Snapshot $snapshot
pwsh -NoProfile -File .\scripts\owner-memory-backup.ps1 -Mode restore-new -Snapshot $snapshot
```

Expected results: `ENCRYPTED_SNAPSHOT_CREATED`, `AUTHENTICATED_SQLITE_BACKUP_VALID` and `RESTORED_TO_NEW_PRIVATE_PATH`.

The proof copy stays in the private backups folder, not Git. The original database and DPAPI key files are unchanged. Do not copy backups or keys into GitHub.

This validates restoration only with the same Windows user/key context. **Disaster recovery after device loss is NOT yet qualified**. Production still requires a separate secure key-recovery plan, data retention/deletion controls, complete relationship history and end-to-end governance. No autonomous sending is provided.
