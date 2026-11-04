---
name: leadership-discovery
description: Map executive accountability for each specific organizational initiative or hiring mandate.
---
# leadership-discovery

**V2.1 authority:** Read `../../../references/career-intelligence-operating-contract-v2.1.md` and `../../../config/operating-policy.json` before use. Project `PERSONAL_CAREER_OUTREACH` is personal permanent leadership employment only. This skill cannot certify source truth, run owner-only DPAPI tools, approve sending, auto-apply or change policy. `SEND_AUTHORIZED` remains BLOCKED.

## Procedure

Identify six distinct relationship functions as relevant: STRATEGIC_SPONSOR, BUSINESS_OUTCOME_OWNER, AI_OR_TECHNICAL_EXECUTION_OWNER, PRODUCT_PORTFOLIO_OWNER, HIRING_SPONSOR and INTRODUCER. A person may hold several roles, but each person-to-initiative edge needs its own evidence. DOCUMENTED requires a visited source explicitly connecting that person to the initiative or hiring decision. A current CIO/CTO/CEO title without that connection is FUNCTIONALLY_PLAUSIBLE or UNKNOWN, never established sponsorship.

Verify person identity, organization affiliation and up-to-date role separately. Before promoting CURRENT affiliation, search for departures, recent role changes, and independent contradictory sources. A recently retrieved old/undated official biography is not sufficient when a newer credible source describes the person as former; record both sources and mark SOURCE_CONFLICT/CURRENT_EXECUTIVE_AFFILIATION_CONFLICT until reconciled. Distinguish an industry advisor or introducer who previously worked at the employer from a current internal decision-maker. Do not silently erase the former employee as a potential relationship, but do not assign them the employer initiative. No guessed hiring power or contact route. Strong strategic research or an official hiring vacancy may be preserved with an unknown executive and marked EXECUTIVE_OWNER_UNVERIFIED; do not invent a name to fill the packet. Output sourced responsibility graph and prioritized research questions.

## Select the right person for a conversation

For each of the three prioritized employer objectives, systematically investigate up to three plausible leaders (e.g. responsible VP/Director, CIO/CTO/CAIO, business-unit head). Assess separately: (1) reliable CURRENT employer/title evidence; (2) directly documented responsibility for the exact initiative or a clearly marked FUNCTIONALLY_PLAUSIBLE relationship; (3) whether the person has enough influence to discuss a bounded internal AI/product leadership contribution; and (4) an attainable, lawful professional route. Prefer the leader closest to the business decision with realistic access; do NOT default to CEO prestige or claim a VP is a hiring sponsor without evidence.

Return one PRIMARY leader plus at most one ALTERNATE when supported. For each, give current-role source, initiative-responsibility source or UNKNOWN, selection rationale, role confidence, and unresolved changes/departures. A current official title is not itself proof of initiative ownership, budget, hiring influence, or interest. If no safe name survives checks, keep the organization as EXECUTIVE_OWNER_UNVERIFIED instead of inventing a person.

## Output boundary

Return only cited facts, clearly marked hypotheses and reason-coded HOLDs. Record whether this specialist was natively selected, NOT_VERIFIED, or SKIPPED_NOT_APPLICABLE. Research findings and drafts are not contact-ready or sent.

## V2.2 candidate hardening — supervised opt-in only

Read `../../../references/career-intelligence-operating-contract-v2.2.md` and `../../../docs/CAREER_V22_MASTERING_GATES.md` only when explicitly running the V2.2 pilot. After identifying a specific complementary leadership responsibility, map business outcome, product portfolio, AI platform, transformation and hiring owners separately. Confirm current affiliation and exact initiative responsibility; a high executive title alone does not establish sponsorship. Search contradictory departures. Native activation and source truth require independent proof. Neither a skill text read nor this instruction grants contact, drafting, sending, applications, private-memory access, or production authority.

For conflicting current-employer role reports that do not assert a definitive departure, record an explicit `conflicts` list with the contradicted `CURRENT_EXECUTIVE_ROLE` claim ID, the same `subject_id` and `object_id` employer ID, and source-specific excerpt. This also produces a conservative affiliation HOLD without rewriting a role-change report as `EXECUTIVE_AFFILIATION_ENDED`. Unsupported prose without an explicit conflict edge cannot independently establish departure; route it to source-review HOLD rather than silently inventing semantics.
