# Career Intelligence V2.2 — End-to-End Hardening and Mastery Gates

**Status: IMPLEMENTATION IN PROGRESS — NOT MASTERED / NOT FIELD-TESTED / NOT PRODUCTION.**

This document is the authority for the draft \`feat/career-intelligence-v2-2-e2e-hardening\` branch and is deliberately distinct from the V2.1 primary runtime on PR #25. V2.2 is **opt-in for synthetic and supervised read-only research**. Do not activate a scheduler, replace \`main\`, approve contact, or migrate live memory based on this branch.

## Why a unified change is needed

V2.1 safely separates source claims from contact authority but its old \`pipeline.make_brief\` remains the optional API researcher. The Codex host performs actual live research, then a separate offline JSON preflight checks format. Earlier field rehearsals surfaced a lost Optum director requisition, a stale Roche executive biography, weak executive-specific contribution theses, and missing professional contact paths. Passing offline CI does not prove that host research, source truth, native skills, protected memory, owner review, and career utility work together.

## Closed as implementation artifacts (not field proof)

| Gap | Implementation evidence | Current assurance |
|---|---|---|
| Policy research state drift | \`config/operating-policy.json\` now matches V2.1 evaluator state enums, including \`DISCOVERED\` | Static/offline tests only |
| Nested V2.2 evidence/schema weakness | \`schemas/career-opportunity-v2.2.schema.json\` enforces bounded nested opportunity, claim, executive, hiring and career-value objects | Structural validation, not source truth |
| Weak leadership contribution specificity | \`outreach_agent/career_contribution.py\` requires a bounded responsibility, candidate capability references, maturity, complementary role, limitations, and business trigger | A strong result is a reported HYPOTHESIS, not a vacancy or confirmed leadership need |
| Missing cross-run opportunity continuity | \`outreach_agent/career_run_ledger.py\` stores immutable user-owned public-research snapshots; missing prior opportunity => NOT_OBSERVED_THIS_RUN | No verified historical-source freshness or trusted identity authority |
| Versioned offline V2.2 handoff | \`scripts/assess_career_opportunities_v22.py\` validates and evaluates current records, optionally reconciles private run snapshots, and emits explicit stage assurance | Structural CLI, NOT native E2E |
| Safe feedback proposals | \`outreach_agent/career_owner_learning.py\` diagnoses repeated human rejections and proposes changes without applying policy or triggering outreach | Caller-supplied decisions not independently authenticated |

## E2E remediation still required — hard release blockers

1. **Native Codex host integration.** Build/observe a single host-supervised workflow with explicitly traced required/conditional skill activation, source-stage outputs, error recovery and evaluator linkage. The structural \`skill_trace\` module must not be used as native proof.
2. **Independent primary-source witness.** \`page_read_success\`, quotations, current roles, and ATS status are caller-supplied metadata. A trustworthy independent witness or directly checked human source review must attest sources before any verified research claim. No fake receipt/self-assertion can be promoted.
3. **Actual contribution usefulness.** Machine fields cannot establish whether the candidate could meaningfully contribute. Owner should judge a bounded internal leadership responsibility, complementarity to existing product leadership, timing, geography and domain limitations.
4. **Protected owner decision history.** V2.2 research snapshot is NOT an encrypted relationship/approval database. Integrate append-only owner judgments through a qualified owner-controlled protected interface, without migrating or reading the live database from Codex.
5. **Trusted person history/opt-out.** Preserve Windows DPAPI owner-only control; new owner-handoff or trusted broker must be separately authorized, tested on an isolated recovered copy, and fail closed on unknown identity, novelty, and route.
6. **Contact-route reality.** An identifiable profile != permission to message. Current affiliation, initiative ownership, route identity, opt-out, and prior relationship must be checked separately.
7. **Operational and recovery.** Resume interrupted host runs without dupes; audit private artifacts, source outages, Phoenix calendar boundaries, backup/restore, crashes and no unauthorized side effects.
8. **Owner-feedback learning persistence.** Pure proposal logic exists, but qualified owner-event ingestion, per-opportunity continuity, and reversible policy review are not yet integrated.
9. **Schema and skill migration.** All fourteen skills, host runner, V2.2 schema, machine policy, public-only report, and negative tests must agree before activating V2.2. Do not silently switch the legacy CLI.
10. **P4/P5 release proof.** Supervised genuine E2E pilot, independent owner judgments, seven real daily cycles, >=40 reviewed real people, correct memory/recovery, and zero unauthorized actions. Code and synthetic tests cannot substitute.

## Mastery sequence BEFORE a fresh live search benchmark

**Gate M0 — Code and contract mastery.** All policy/code/schema enums consistent. V2.1 compatibility/19-column person exporter preserved. No forbidden data in public Git, no sender, no auto-application. All offline tests and adversarial cases run on Windows and Ubuntu.

**Gate M1 — Synthetic integrated host rehearsal.** Confirm Codex actually selects the orchestrator/specialists or honestly NOT_VERIFIED; genuine source witness/access, complete stage trace, duplicate/failed-source recovery, executable offline handoff and no private memory access.

**Gate M2 — Owner-trusted memory and review rehearsal.** Only normal owner-controlled Windows environment with isolated restored **test copy** and explicit owner authorization. Validate identity binding, suppressions, previous meetings, owner decision event integrity and recovery. Never provide keys to Codex.

**Gate M3 — Fixed-case comparison.** Replay Banner, TEP, Roche and Optum as historical controls: complementary leadership rather than generic AI pitch; current vs former executive; current executive with/without initiative ownership; both Optum requisitions preserved. The source truth must be independently reconfirmed.

**Gate M4 — Fresh blinded field benchmark.** Preselect six NEW employers before sourcing (three strategic and three direct hiring), preserve every employer and all distinct opportunities. Owner reviews actual contribution value. Keep holds and honest shortfalls. No contact or applications.

**Gate M5 — Production qualification.** Seven true consecutive source-backed daily cycles, >=40 human-reviewed people, monitoring, protected recovery and explicit release review. Native P4/P5 must be evidenced or production remains NO-GO.

## Invariants never relaxed

- Personal permanent internal leadership employment; never Nova sales/capture/subcontracting.
- Tucson-first, feasible U.S.-remote, all industries, 60% AI/transformation vs 40% enterprise product capability **directional**, not a quota.
- A business trigger or recent appointment does not prove staffing need.
- One organization may contain many requisitions, initiatives, potential executive relationships.
- Prior missing opportunity stays remembered with last observed status; never silently deleted/closed.
- Direct official ATS route is independent of manager sponsorship.
- Owner PURSUE is only an instruction to research, not consent for a message or application.
- \`contact_ready=false\`, \`send_authorized=false\`, \`application_submitted=false\` from research.
- Gate A exact draft approval and Gate B independent transmission authorization remain distinct; current software SEND_AUTHORIZED blocked.
- Neither source claims, operator decisions nor host skill invocations are self-authenticating.

## Engineering definition of DONE

**Implementation done** means: all numbered gaps have a named code/host component, tests, and reviewed operational handoff; the static validator and CI pass; no outstanding P0/P1 defect; compatible data migration plan documented; all fourteen skills are aligned. **Mastery done** means implementation *plus* actual adversarial host behavior, source witness, owner-private recovery and human relevance evidence. **Production done** separately requires M5. Never report one status as another.

Reference: \`evals/EVALUATION_PLAN.md\`, \`docs/PRODUCTION_PLAN.md\`, \`references/career-intelligence-operating-contract-v2.1.md\`.

## Trusted owner handoff — implementation progress, not field proof

The draft includes outreach_agent/career_source_witness.py (allowlisted independent bounded HTTPS page-text reproduction), outreach_agent/career_owner_journal.py (key-bound exact packet and source-receipt research preference journal), scripts/owner_career_v22_handoff.py and scripts/owner-career-v22.ps1 (interactive Windows DPAPI owner-only source-check and private-history/decision process), plus advisory-only verified-journal learning. The source receipt states semantic truth is UNVERIFIED and contact_ready=false. The journal cannot authorize outgoing actions. The Codex research stage is still host-manual; supported host native-skill events must be observed separately. An HMAC under local DPAPI keys proves possession of keys in the session, not independently verified human identity. No real owner Windows execution, restored copy test, external source fetch, recovery drill, off-device journal checkpoint, or complete E2E host trace is established by CI.
