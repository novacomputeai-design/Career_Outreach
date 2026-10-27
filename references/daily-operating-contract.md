# Daily run contract
Target 20 verified **new** individual contacts per day (not messages sent). Source research may need many more raw candidates; do not assume any source volume guarantees yield.

## Required inputs
Resume-derived profile; date in America/Phoenix; authorized current research tools; private persistent relationship state; optional user-approved prior conversations. The repository itself is PUBLIC and must not store private history.

## Workflow
1. **Organization discovery:** Rotate sectors, Tucson tech parks, employers, innovation ecosystems, company sites, associations, plus US remote prospects. Find actual organizational initiatives or opportunities; source URLs and dates.
2. **Leadership discovery:** Identify real people with plausible professional connection, differentiate verified hiring authority from suspected hiring influence vs strategic introduction.
3. **Contact verification:** Independently corroborate person/current position, record primary sources/recency, verify permitted professional route. Explicitly mark indirect route vs direct route.
4. **Qualification:** Apply `references/scoring-rubric.md` and mandatory hard gates. Topic must be interesting to both parties, not simply a cold job request.
5. **Memory:** Deduplicate across runs by person identity; prevent previously approached/suppressed contacts from being labeled new.
6. **Outreach preparation:** Personalize a draft for user review, never send automatically. Draft-content approval is not permission to transmit.
7. **Daily brief:** Top 20 eligible NEW people ranked with full sources, why connect and next action; existing follow-ups reported separately; shortfall and limitations explicit.
8. **Quality audit:** Independently review evidence, score arithmetic, novelty, privacy and authorization state.

## State definitions
DISCOVERED -> VERIFIED -> QUALIFIED -> CONTACT_READY -> DRAFTED -> DRAFT_APPROVED -> SEND_AUTHORIZED -> CONTACTED -> REPLIED -> MEETING -> FOLLOW_UP_PENDING -> CLOSED. Alternative states: HOLD_UNVERIFIED, DUPLICATE, SUPPRESSED, OPTED_OUT, NOT_RELEVANT.
Only observed human acts can authorize outbound transmission. If durable private history is unavailable, output novelty=UNVERIFIED and 0 confirmed NEW; do not presume an unfamiliar person was never contacted.

## Expected brief counters
date / target / considered / verified / qualified / confirmed new contact-ready / duplicates / excluded / follow-ups / source access gaps / quota shortfall / skill activation mechanism / outbound activity (always 0 unless separately authorized).

## Runtime boundary
SKILL.md is a procedure, NOT a scheduler, API connection or CRM. A real daily run needs authorized search, private storage, an agent host, a scheduler, logs, independent testing and a human approval UI. CI only tests repository integrity.
