# Daily run contract

**Authority:** `config/operating-policy.json` v0.2.2; `docs/PRODUCTION_PLAN.md`. Memory screening and deterministic governance are mandatory early release gates; written policy is not equivalent to live enforcement.
Target 20 verified **new** individual contacts per day (not messages sent). Source research may need many more raw candidates; do not assume any source volume guarantees yield.

## Non-negotiable scope preflight
Before processing candidates or publishing a brief, verify project ID `PERSONAL_CAREER_OUTREACH` and career networking purpose. Reject cross-project sales, federal subcontracting pursuits, RFQs, bid capture and supplier onboarding. Treat scope ambiguity as HOLD for human review and never count it toward 20.

## Mandatory scope preflight
Every candidate requires project ID `PERSONAL_CAREER_OUTREACH` and an individual-career networking rationale. Cross-project subcontracting, commercial sales and procurement pursuits are HOLD; never report them as career contacts.

## Required inputs
For opportunity discovery: resume-derived public-safe profile; date in America/Phoenix; authorized current public research tools. Private relationship state is not required to discover or rank opportunities. For contact-ready people counts, private persistent relationship state and the other mandatory policy gates remain required. Supervised research-only work may proceed without memory access, but novelty must remain UNVERIFIED and confirmed-new/contact-ready counts remain zero. The repository itself is PUBLIC and must not store private history.

## Workflow
1. **Opportunity discovery:** Find direct-hiring leadership roles and evidence-backed strategic opportunities; source and date the need, assess the candidate against actual requirements or a bounded contribution, and compare related roles/initiatives within each organization.
2. **Opportunity ranking:** Rank opportunity quality before researching people. Preserve strategic leads without claiming vacancies. Do not use contactability, private novelty, or contact-ready status as opportunity-quality factors.
3. **Leadership discovery:** For selected opportunities, compare relevant operating leaders, sponsors, hiring-process contacts, and role promoters; differentiate documented authority from plausible influence.
4. **Contact and relationship checks:** For the selected people, verify identity, role, permitted person-specific route, novelty, and suppression through the authorized operator-side process. Missing history blocks novelty/contact readiness, not the opportunity assessment.
5. **Person qualification and governance:** Apply `references/scoring-rubric.md` only to person-to-person contact qualification and enforce all existing hard gates.
6. **Conditional preparation:** Draft only if requested and eligible for review. Draft-content approval is not permission to transmit. Follow-up and conversation preparation apply only when warranted.
7. **Quality audit:** Audit opportunity ranking separately from evidence, identity, route, novelty, privacy, and authorization before reporting.
8. **Daily brief:** Show ranked opportunities first, then associated people/routes/holds. Keep opportunity counts separate from up to 20 independently human-reviewed NEW contact-ready people and all existing follow-ups.

## State definitions
DISCOVERED -> VERIFIED -> QUALIFIED -> CONTACT_READY -> DRAFTED -> DRAFT_APPROVED -> SEND_AUTHORIZED -> CONTACTED -> REPLIED -> MEETING -> FOLLOW_UP_PENDING -> CLOSED. **Target state machine only:** CONTACT_READY and SEND_AUTHORIZED are not production-qualified. The current implementation hard-blocks SEND_AUTHORIZED pending trusted history, verified recipient/route and human-operator authentication. Alternative states: HOLD_UNVERIFIED, DUPLICATE, SUPPRESSED, OPTED_OUT, NOT_RELEVANT.
Only observed human acts can authorize outbound transmission. If durable private history is unavailable, output novelty=UNVERIFIED and 0 confirmed NEW; do not presume an unfamiliar person was never contacted.

## Expected brief counters
date / organizations screened / opportunities found and ranked (direct-hiring vs strategic-exploration) / related within-organization alternatives compared / target / people considered / verified / qualified / confirmed new contact-ready / duplicates / excluded / follow-ups / source access gaps / quota shortfall / skill activation mechanism / outbound activity (always 0 unless separately authorized). Opportunity counts never contribute to the person target.

## Runtime boundary
SKILL.md is a procedure, NOT a scheduler, API connection or CRM. A real daily run needs authorized search, private storage, an agent host, a scheduler, logs, independent testing and a human approval UI. CI only tests repository integrity.
