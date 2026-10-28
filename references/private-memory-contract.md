# Private relationship memory and identity
The Git repository, whether public or private, must not hold real relationship history. Private state must be protected by the agent runtime, with lawful access and user controls.

For each person track stable ID, verified official profile URL (if available), normalized name, organization changes, aliases, source history, professional contact route, last verification, prior outreach attempts, message-content approval, separate send permission, replies, meetings, opt-out, next-step notes and run IDs.

Novelty checks use person-level identity, not organization only. Treat same name with different employer as possible prior human; research rather than creating a new unique record. Cross-run suppression is mandatory. Existing relationships belong in follow-up queue, not 20 new people. Missing history -> novelty unknown -> zero **confirmed** new.

Private records should use least privilege, encryption as applicable, retention policy, user-access permissions, and backups; no plain-text CRM dumps into CI artifacts or GitHub issues.


## Operator-only Windows private lookup (Codex sandbox restriction)
`scripts/relationship-check.ps1` may be run by the trusted operator in their normal Windows PowerShell session, not by Codex. Owner-context DPAPI lookup passed, but Codex sandbox direct execution failed. Never weaken Windows sandbox, change DPAPI scope, print keys, or grant the agent access to private credentials. Until a narrowly scoped broker is qualified, Codex accepts only minimal operator-approved classifications labeled OPERATOR-PROVIDED, not full-history reconciliation. NOT_FOUND_IN_LOCAL_STORE remains UNVERIFIED. Never import/export private records into the repository.

FIRST_LEARNED is a user-reported first discovery, not independent verification and not proof of outreach history outside the local store. PREVIOUSLY_MET means user-reported existing relationship. Previously seen candidates do not count as a new discovery in later runs, even when not previously contacted. The gateway has no write/import functions or send mechanisms.

See `docs/PRODUCTION_PLAN.md` and the versioned `config/operating-policy.json`. This contract is not itself evidence of enforcement.
