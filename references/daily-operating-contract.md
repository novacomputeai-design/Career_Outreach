# Daily run contract

**Authority:** `config/operating-policy.json` v0.2.2; `docs/PRODUCTION_PLAN.md`. Memory screening and deterministic governance are mandatory early release gates; written policy is not equivalent to live enforcement.
Target 20 verified **new** individual contacts per day (not messages sent). Source research may need many more raw candidates; do not assume any source volume guarantees yield.

## Non-negotiable scope preflight
Before processing candidates or publishing a brief, verify project ID `PERSONAL_CAREER_OUTREACH` and career networking purpose. Reject cross-project sales, federal subcontracting pursuits, RFQs, bid capture and supplier onboarding. Treat scope ambiguity as HOLD for human review and never count it toward 20.

## Required inputs
Resume-derived profile; date in America/Phoenix; authorized current research tools; private persistent relationship state; optional user-approved prior conversations. The repository itself is PUBLIC and must not store private history.

## Workflow
1. **Organization discovery:** Rotate sectors, Tucson tech parks, employers, innovation ecosystems, company sites, associations, plus US remote prospects. Find actual organizational initiatives or opportunities; source URLs and dates.
2. **Leadership discovery:** Identify real people with plausible professional connection, differentiate verified hiring authority from suspected hiring influence vs strategic introduction.
3. **Early private memory screen:** compare identities with prior discoveries, contacts, existing relationships and opt-outs in trusted operator-side process; unavailable history => HOLD_UNVERIFIED.
4. **Contact verification:** Independently corroborate person/current position, record primary sources/recency, verify permitted professional route. Explicitly mark indirect route vs direct route.
5. **Qualification:** Apply `references/scoring-rubric.md` and mandatory hard gates. Topic must be interesting to both parties, not simply a cold job request.
6. **Final memory and governance gate:** recheck private history and policy, including name collisions, source/route evidence and prior discoveries; no skill can override HOLD/REJECT.
7. **Outreach preparation:** Personalize a draft for user review, never send automatically. Draft-content approval is not permission to transmit.
8. **Quality audit:** Independently review evidence, score arithmetic, novelty, privacy and authorization state **before** the brief.
9. **Daily brief:** Report up to 20 independently human-reviewed NEW contacts, source-corroborated pending reviews, prior discoveries and follow-ups separately, true shortfalls and blocked checks.

## State definitions
DISCOVERED -> VERIFIED -> QUALIFIED -> CONTACT_READY -> DRAFTED -> DRAFT_APPROVED -> SEND_AUTHORIZED -> CONTACTED -> REPLIED -> MEETING -> FOLLOW_UP_PENDING -> CLOSED. **Target state machine only:** CONTACT_READY and SEND_AUTHORIZED are not production-qualified. The current implementation hard-blocks SEND_AUTHORIZED pending trusted history, verified recipient/route and human-operator authentication. Alternative states: HOLD_UNVERIFIED, DUPLICATE, SUPPRESSED, OPTED_OUT, NOT_RELEVANT.
Only observed human acts can authorize outbound transmission. If durable private history is unavailable, output novelty=UNVERIFIED and 0 confirmed NEW; do not presume an unfamiliar person was never contacted.

## Expected brief counters
date / target / considered / verified / qualified / confirmed new contact-ready / duplicates / excluded / follow-ups / source access gaps / quota shortfall / skill activation mechanism / outbound activity (always 0 unless separately authorized).

## Runtime boundary
SKILL.md is a procedure, NOT a scheduler, API connection or CRM. A real daily run needs authorized search, private storage, an agent host, a scheduler, logs, independent testing and a human approval UI. CI only tests repository integrity.
