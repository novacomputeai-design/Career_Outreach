# Private relationship memory and identity
The Git repository, whether public or private must not hold real relationship history. Private state must be protected by the agent runtime, with lawful access and user controls.

For each person track stable ID, verified official profile URL (if available), normalized name, organization changes, aliases, source history, professional contact route, last verification, prior outreach attempts, message-content approval, separate send permission, replies, meetings, opt-out, next-step notes and run IDs.

Novelty checks use person-level identity, not organization only. Treat same name with different employer as possible prior human; research rather than creating a new unique record. Cross-run suppression is mandatory. Existing relationships belong in follow-up queue, not 20 new people. Missing history -> novelty unknown -> zero **confirmed** new.

Private records should use least privilege, encryption as applicable, retention policy, user-access permissions, and backups; no plain-text CRM dumps into CI artifacts or GitHub issues.


## Scoped Codex read-only lookup
Codex may call `pwsh -NoProfile -File .\scripts\relationship-check.ps1 -PersonName "Individual Name"` with a person explicitly being researched. The script loads existing DPAPI keys only within an isolated PowerShell process, calls the Python CLI via a SQLite **read-only** connection, and returns a minimal classification; it never prints keys. Run no arbitrary SQL, bulk data exports, or direct plaintext-key inspection. The script cannot prevent arbitrary code with the same Windows user permissions from accessing the underlying files; Codex tool permission and prompt-injection boundaries still matter. Never treat no match as proof of complete prior-contact history.

FIRST_LEARNED is a user-reported first discovery, not independent verification and not proof of outreach history outside the local store. PREVIOUSLY_MET means user-reported existing relationship. Previously seen candidates do not count as a new discovery in later runs, even when not previously contacted. The gateway has no write/import functions or send mechanisms.
