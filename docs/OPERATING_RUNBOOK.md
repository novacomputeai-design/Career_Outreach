# Daily executive outreach runbook

**Production authority:** `config/operating-policy.json`, `docs/PRODUCTION_PLAN.md` and `docs/GAP_CLOSURE_MATRIX.md`. Memory and governance are **early mandatory gates**. Codex is the chosen agent; the Tavily/OpenAI API runner is optional legacy.

## Mission and metrics
Primary objective: career-relevant leadership conversations, not mass messaging.
Research target: **up to 20 new source-corroborated prospects each daily run**. Human-review-approved contact-ready count is separate and can be zero. Contacted, replied, met, introduced, opportunity and hired are distinct observed outcome metrics; never infer progress from drafted messages.

The current live pipeline is only a pilot; no completed external seven-day behavioral evaluation exists. The owner independently completed the live backup-first governance schema migration on 2026-10-28, but trusted Codex history reconciliation and CONTACT_READY remain blocked.

## Governance enforcement status

The selected Codex agent may propose leads but cannot self-certify human review, role truth or novelty. The optional Python local store now applies a **structural source and suppression precheck** to `review-contact` and requires a recorded review plus a structurally valid record for `approve`. Both permitted and denied review/approval actions are stored in a protected versioned governance audit. `governance-audit` displays minimal decision metadata to the owner only. These are the first P3 enforcement controls, **not** end-to-end CONTACT_READY certification or independent authentication of the command operator. Separate human draft approval remains required. The `SEND_AUTHORIZED` **record transition is currently blocked**, even after content approval, because recipient, route, private-history novelty and authentic operator authorization are not yet independently qualified. Do not interpret a saved draft as permission to send. Existing relationships need a dedicated follow-up approval path; do not treat them as NEW to bypass the gate.

## Report counting assurance

The local `run-readiness` command reports only the count of **recorded operator-attested source/route/fit reviews**. Those records are not independently authenticated reviewer identities and are not full private-history novelty reconciliation. The output deliberately fixes `new_contact_ready=0` and `production_verified_contact_ready=0` until a separate governed, verifiable promotion mechanism is implemented and qualified. Do not convert these review counts into the daily 20 new contacts quota.

## Owner-controlled identity handoff

Use `docs/OPERATOR_BATCH_SCREENING.md` for private-read-only name/profile matching and `scripts/reconcile_operator_screening.py` for exact batch binding. This bridge never certifies cross-channel novelty, authenticates an approver, or runs DPAPI inside Codex. Treat `NOT_FOUND_IN_LOCAL_STORE` as HOLD and keep all contact-ready counts at zero until outside history is independently reviewed. Public screening files and operator reports must remain outside Git.

## Review queue
1. Open the latest private report (NEVER check into Git). Search the candidate's primary and independent secondary sources again.
2. Confirm the person holds the current role, their organization is correct, the topic is relevant to Fadi's real resume experience and the contact pathway is realistic for that individual.
3. An organization contact form is marked INDIRECT and might not reach the named executive. Do not approve its reachability by assumption.
4. Use the dedicated human review command only when source, role, reason and route truly satisfy expectations.
5. Approve draft content separately. If you choose to send externally, authorize sending as an independent action specific to the recipient/draft. No emailing/LinkedIn sender is implemented in this code.
6. Enter actual CONTACTED and subsequent observed outcome events in the private database; record opt-outs.
7. Inspect outcome intelligence after meaningful observations. Query-priority suggestions require a user decision; they do not change the qualifying score or exclude industries.

## Evidence and incident handling
- For Codex-native research, verify authorized live browsing, not Tavily/OpenAI API credentials; missing web access => HOLD.
- Private relationship checks execute ONLY in the owner's trusted PowerShell context until a secured broker qualifies. Codex sandbox DPAPI failure must not be bypassed.
- Source failure => status PARTIAL_SOURCE_FAILURE or COMPLETE_WITH_SOURCE_ERRORS; inspect private report/log and do not assert full market coverage.
- Interrupted output => use restore-report to recover the latest completed private report from encrypted state.
- Duplicate or changed employer => identity HOLD until reconciled; suppress opted-out people.
- Source discrepancies, old bios or guessed addresses => HOLD, not counted to target.
- Keep database, backup and encryption key outside repo; independent secure retention and access review required.
- No automatic sends. Never commit personal outreach text, replies or relationship logs to public GitHub.

## Seven-day field qualification
At each daily run preserve (private) run ID, provider status, queries/results and costs, source review decisions, scored candidate list, duplicate counts, actual new human-reviewed count, and discovered errors.
Independently review >=40 people across at least two relevant organization sectors and Tucson/remote categories. Measure percent YOU would actually consider contacting and why. Verify all currently defined adversarial evaluation cases, including stale role, namesake, previous contacts, opt-out, missing sources, injected source instructions and draft-vs-send separation.
Native skills must be explicitly selected using the actual host's skill mechanism and the selection trace recorded. The Python pipeline simulates stage responsibilities but is not proof of native skill selection.
Do not claim production readiness until real data and runtime reliability are demonstrated.

## Business outcome hypothesis
As a hypothetical scenario, 20 personally approved sends a day (not automatically sent by this system) can produce conversations, introductions and potential career opportunities, but no response, meeting, referral or hiring rates are established. Assess whether 20 new daily people is sustainable after actual data.
