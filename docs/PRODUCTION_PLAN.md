# Career Outreach — Production Plan (authoritative sequence)

Status date: 2026-10-28. **NOT PRODUCTION QUALIFIED.**

## Goal and execution authority

Personal executive career networking, Tucson/Southern Arizona first, applicable US-remote opportunities and all industries where credible transferable experience exists. Daily research target: **up to 20 new, qualified, genuinely relevant people**; never fabricate quota completion. The principal host is **Codex CLI + 14 local Career Outreach skills**. Python implements deterministic checks and protected local relationship memory. The older Tavily/OpenAI API-based research runner is **optional legacy**, not the chosen execution path; its scripts or scheduler recipes must not be mistaken for the Codex workflow.

**One authority for machine-governed policy:** `config/operating-policy.json` (versioned). All documents, skills, validators, databases and daily reports must conform to it; differences are release blockers. A model's assertion that a check passed is not sufficient evidence that a deterministic runtime gate ran.

## Layered target architecture

1. **Inputs and authorized sources:** public official employers, current verified executive roles, announced initiatives; permitted professional routes. No LinkedIn scraping, guessed email, or private contacts in Git.
2. **Codex agent orchestrator + 14 skills:** organization discovery → leadership discovery → early memory screening → source verification and provenance → relationship qualification → drafting → independent run audit → executive brief. Additional specialist skills for follow-up, meetings and outcome learning as required.
3. **Private memory (cross-cutting):** protected identity / aliases / profiles, source evidence and recency, prior discoveries, previous meetings/contacts, suppressed persons, drafts, approvals, real outcomes, follow-ups and prior run IDs. First learned ≠ previously contacted; first outreach opportunity ≠ first discovery this run.
4. **Deterministic governance (cross-cutting):** policy decision for identity, reliable evidence, official/permitted route, provenance, novelty check, suppression, relevance and score. A PASS for structural research is not human-approved contact readiness. FAIL/HOLD must be visible with reasons. No skill overrides the hard gate.
5. **Human review and authorization:** independently review source claims, contact suitability and novelty; approve draft content per person/draft hash; separately authorize sending of that exact draft. **No autonomous sending and no sender currently integrated.**
6. **Daily brief and controlled learning:** report independently qualified NEW, existing follow-ups, pending reviews, held/excluded, shortfall, actual manual outreach and observed responses. Learning may recommend changes but cannot automatically alter policy, eligibility or sending permissions.

## Early production work (critical path)

| Sequence | Milestone | Acceptance and proof | Current state |
|---|---|---|---|
| **P0** | **Versioned policy baseline + instruction reconciliation** | Single policy authority, consistent `AGENTS.md`, skills, private-memory contract, runbook and operating docs; CI tests detect critical contradictions | **IN PROGRESS** |
| **P1** | **Memory integrity and recovery** | Stable identities, prior discoveries, established contacts, suppression, encrypted data, backup/restore with protected key recovery and Windows tests | **OWNER WINDOWS BACKUP/VERIFY/RESTORE-NEW PASSED; PORTABLE KEY RECOVERY UNQUALIFIED** |
| **P2** | **Governed private batch reconciliation** | Trusted owner-context batch lookup OUTSIDE Codex DPAPI sandbox; bounded input, minimal classification output, namesake/opt-out HOLD, no plaintext keys to Codex; then independently qualify a narrowly scoped broker if truly needed | **OPERATOR BATCH PASSED ON WINDOWS; automatic broker NOT IMPLEMENTED** |
| **P3** | **Deterministic governance enforcement and audit** | Single fail-closed decision module wired to candidate-counting, human review and approval-state transitions; auditable policy version, allow/hold/reject reasons, source and reviewer provenance; adversarial tests | **INITIAL REVIEW/CONTENT GATES CODED; SEND_AUTHORIZED BLOCKED; full enforcement NOT QUALIFIED** |
| **P4** | **Supervised Codex + skills end-to-end pilot** | Real discovery → evidence check → protected memory reconciliation → gate → independent review → quality brief, no sending. Capture host-native specialist evidence if exposed; otherwise NOT VERIFIED | **NOT YET DEMONSTRATED END-TO-END** |
| **P5** | **Production qualification / scheduling** | Seven consecutive actual daily runs, >=40 independently assessed real people, no invented contact-ready counts, recovery/incident drill, monitoring, windows-task qualification appropriate to Codex native path, zero unauthorized sends | **NOT STARTED** |

**Ordering:** P0 → P1/P2 → P3 → P4 → P5. Memory and governance precede any claim of production-grade discovery counts or unattended schedule. Work on source improvements can continue in parallel, but must pass P3.

## Current evidence (not certification)

- Windows Codex CLI 0.164.0 authenticated using ChatGPT. Primary skill invocation reported; specialist native activation is NOT VERIFIED.
- Local offline tests passed; encrypted SQLite persisted preferences and two operator-initiated classifications.
- Trusted ordinary PowerShell DPAPI read-only lookup worked. Identical wrapper **failed from inside Codex sandbox**, likely due to different security identity. **Do not weaken sandbox, change DPAPI protection scope or expose keys to Codex.**
- A five-person supervised Codex web search returned two source-based provisional leads, three held, zero confirmed NEW/contact-ready, zero outreach.
- GitHub CI is offline/structural evidence only. Repo remained PUBLIC at last check; secrets and relationship state are strictly outside it.
- Protected operator-controlled batch memory screening was verified with real owner-context Windows DPAPI lookups (Josh Lee, David Ebert, synthetic unknown). A fully automatic broker, complete cross-channel memory/novelty, retention/deletion, secure recovery and field qualification remain unverified.
- First deterministic stage-specific review and draft-approval guards are implemented with policy-versioned encrypted audit decisions. The local run-readiness report is now fail-closed: manual source/route/fit review counts are separate from confirmed-new contact-ready (always zero until complete novelty and independent human-verification gates are qualified). This is NOT proof of actual human identity, current external source truth, recipient/route-bound send authorization or full CONTACT_READY eligibility. The local SEND_AUTHORIZED transition is fail-closed until those prerequisites are qualified. No sender exists.

## Counter contracts and state distinctions

| Term | Meaning |
|---|---|
| DISCOVERED_THIS_RUN | Person first identified during this specific research cycle (not proof of no prior contact) |
| FIRST_LEARNED | Operator says this was first time learning of the person; may be first-contact opportunity, but already recorded after intake |
| PREVIOUSLY_MET | Operator reports prior relationship; follow-up queue, never NEW discovery |
| SOURCE_CORROBORATED_PENDING_REVIEW | Evidence checked structurally or with sources, but not human-approved |
| NOVELTY_UNVERIFIED | Private memory unavailable or incomplete, or no independent prior-history check |
| NEW_CONTACT_READY | Explicitly human reviewed, source/route/novelty and governance gates passed with per-run evidence |
| APPROVED_DRAFT | Human approved the content of a specific draft; not permission to send |
| SEND_AUTHORIZED | **NOT CURRENTLY GRANTABLE.** It requires separate human permission for an exact person, draft hash and verified route once trusted history and operator controls are qualified. No agent sender exists. |

A person previously discovered in another run cannot be counted as a new discovery again. User-reported first learning does not automatically confer independent review, verified reachability or permission to contact.

## Governance requirements

- **Protect:** encrypted private state, isolated DPAPI credentials, identity digests, least privilege, minimization of shared classifications, protected backups, retention and deletion process.
- **Control:** explicit source and contact-route validation, policy-based eligibility, hard opt-out, duplicate and namesake HOLD, no confidence inflation, no fabricated contact attempts or outcomes, no automatic policy optimization.
- **Audit:** store run ID, individual identity reference (privately), policy version, source URLs/dates, decision state/reasons, manual review provenance and exact-draft authorization history.
- **Human authority:** only operator can approve policy changes, source/route confidence, outgoing draft content, sending, suppression overrides if permitted, recovery or deletion. Agent may never promote itself to approver.
- **Incident response:** halt/mark partial on missing keys, sandbox failure, stale source, disputed identity, source prompt injection, untrusted route, data corruption, unexpected sender action or backup failure.

## Release decision

Only independently reproduced Windows runtime evidence plus observed daily human quality review can close P5. If any mandatory memory/governance gate fails, report HOLD/NOT VERIFIED and honest shortfall; never count or send optimistically. Related engineering tracking: issues #1, #2, #3 and #9.

### Memory recovery compatibility note (2026-10-28)

An earlier owner Windows backup attempt failed because the original private database predates the `governance_decisions` table. The compatibility fix passed **real owner Windows encrypted backup, verification and restore-to-new-file**, all reporting `LEGACY_PRE_GOVERNANCE_AUDIT`. A separately qualified owner-approved **additive governance audit schema migration** must be tested on that recovery copy before any change to the live database. Windows recovery proof is for the existing user account only; portable DPAPI key recovery after loss of account/device remains unqualified.
