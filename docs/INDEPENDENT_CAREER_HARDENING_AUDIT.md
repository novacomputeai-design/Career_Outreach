# Career Outreach — Independent Hardening Audit & Release Gates

**Audit date:** 2026-10-28. **Mission:** personal executive career networking only.
**Authority:** `config/operating-policy.json` (project ID `PERSONAL_CAREER_OUTREACH`, version 0.2.2).
**Disposition:** NOT PRODUCTION QUALIFIED. No autonomous sending, no recruiting/hiring promise, no automatic contact-ready certification.

## Remediation implemented and CI-tested

1. **Project separation:** policy, personal career skill instructions and structural candidate/review gates HOLD explicit federal prime/subcontracting, supplier teaming and business sales purposes. Research briefs and CLI summaries carry the canonical project ID. This is a deterministic tripwire, not proof of all natural-language intents.
2. **Private identity integrity:** each stored person's decrypted name/profile must recompute the stored HMAC digests with the supplied identity key. A mismatched identity key cannot make old people disappear silently. This does not establish complete history in unconnected emails or professional networks.
3. **Schema safety:** writable open of an existing pre-governance DB refuses implicit schema creation. Only the separate owner-approved, authenticated encrypted backup-first migration may add the audit table. No live migration is performed by CI, code changes or Codex.
4. **Outreach quality:** optional Python researcher requires at least one dated role source across its two role sources; undated/undated combinations HOLD. Per-source recency is reported as evidence, never current-employment certification. Provisional heuristic scores can express >=85 for strongly supported leadership-fit while retaining rubric caps. Unsent drafts now include a specific organization initiative and conversation rationale instead of a generic template.
5. **Prompt/report controls:** sourced-only claims, observed source access and role uncertainty remain visible; copied business capture entries must not be imported to this career agent. No API key, private store, DPAPI key, or real contact data entered the public repository.
6. **Known safety fence:** `SEND_AUTHORIZED` is unconditionally HOLD. Operator attestation is not independently authenticated and the runtime has no sender. Source-corroborated review and saved draft content do not grant contact readiness.

## What has been independently observed (not reproduced by GitHub CI)

- Owner-Windows protected DPAPI relationship lookup and batch screening work in ordinary PowerShell, not in Codex's sandbox.
- Same-user Windows encrypted memory snapshot, authentication verification and restore to new private SQLite file passed.
- The recovered **test copy**, not the live private database, passed explicit additive governance schema migration with unchanged original row counts.
- Supervised Codex public-source research was reported earlier, but specialized native skill-selection/activation and complete public-to-private-to-reviewed execution were not independently qualified.

## Open release blockers — none may be waived by a model

| Gate | Required objective evidence | Status |
|---|---|---|
| Windows P0 regression | Pull latest main, run policy validators and full synthetic tests in ordinary user shell; read-only protected relationship batch still works | PENDING OWNER PROOF |
| Private live schema | Inspect original live DB READ-ONLY; separately approved, backup-first live migration after owner decision; recheck known identities and audit | NOT EXECUTED |
| Portable recovery | User-approved protection and recovery of original Fernet and HMAC identity keys across lost Windows account/device, without publishing or passing to Codex | NOT QUALIFIED |
| Complete novelty | Private identity aliases and historical contacts/discoveries, external history sources with access and provenance; missing history -> 0 verified NEW | NOT QUALIFIED |
| Current role/route | Independent person/source verification, permitted route checks, freshness and actual relevance reviewed by operator | NOT FIELD QUALIFIED |
| Human authorization | Authenticated operator review and per-recipient route/content binding; never permit self-approved sending | NOT QUALIFIED; SENDING BLOCKED |
| Native Codex | Record actual `/skills` or supported invocation evidence of orchestrator and 13 specialists; do not confuse file reads with activation | NOT PROVEN |
| P4 supervised real run | Personal-career-only research -> source/route evidence -> protected history -> HOLD/review -> brief -> human evaluation; no messages | NOT COMPLETED |
| P5 reliability | 7 consecutive real daily cycles, >=40 independently reviewed real individuals, zero unauthorized actions, recovery drill and monitoring | NOT COMPLETED |

## Measurable acceptance criteria

A correct daily brief MUST show the career project ID, America/Phoenix date, no more than 20 genuine independently reviewed new people, transparent unverified/held/rejected records and shortfall, separate existing relationships/follow-ups, source URLs and dated claims, true indirect/direct/manual contact-route labels, explicit UNSENT draft status, and no implicit sending approval. Until novelty and authenticated human review gates are qualified, **production_verified_contact_ready = 0** regardless of research volume.

Project-boundary adversarial test: presenting a realistic-looking Nova federal award/subcontracting lead as an executive career recommendation must be rejected. A self-declared career project ID accompanying commercial intent must also HOLD. This is a defense-in-depth rule, not permission to copy data from another project.

**Release rule:** Passing CI or a successful synthetic test is necessary but insufficient. The P4/P5 gates require real user-supervised field evidence before production scheduling. Do not unconditionally schedule a fallback API/Python runner and claim it is the Codex-native 14-skill workflow.

## Windows regression remediation — 2026-10-28

Owner Windows PowerShell first validated skill and governance structure but its 95-test suite reported 14 ERROR outcomes. The causes were unavailable IANA timezone data for `America/Phoenix` (6 cases) and unclosed synthetic `sqlite3.connect()` handles locking ephemeral databases on Windows during temporary-directory cleanup (8 cases). This was not evidence of real relationship database corruption. The patch adds the `tzdata` runtime dependency plus a strictly contemporary Phoenix UTC-07:00 fallback when the host has no zoneinfo database, closes each synthetic SQLite connection explicitly, and requires Windows as well as Linux GitHub Actions validation. Owner Windows re-test is still REQUIRED before marking this operationally qualified.

Safe owner verification after merge (normal PowerShell, no Codex/DPAPI keys): `python -m pip install -r requirements.txt`, then both structural validators and `python -m unittest discover -s tests -q`. No live migration, contact lookup, outreach or sending is part of these tests.
