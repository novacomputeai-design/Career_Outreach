---
name: contact-verification
description: Verify professional person-specific contact and official employer application routes without guessing addresses.
---
# contact-verification

**V2.1 authority:** Read `../../../references/career-intelligence-operating-contract-v2.1.md` and `../../../config/operating-policy.json` before use. Project `PERSONAL_CAREER_OUTREACH` is personal permanent leadership employment only. This skill cannot certify source truth, run owner-only DPAPI tools, approve sending, auto-apply or change policy. `SEND_AUTHORIZED` remains BLOCKED.

## Procedure

Current executive name, affiliation and role require evidence separate from initiative responsibility. Resolve newer departure/conflicting-employer evidence before evaluating a person-specific route. A former employee or outside advisor is not a current internal employer decision-maker. A public platform profile URL is at most a possible MANUAL person-specific route after identity/profile verification; it is neither a warm introduction, a confirmed reachable inbox, nor outreach authorization. Identify legitimate WARM_INTRO, DIRECT or MANUAL person-specific route with supporting source; INDIRECT_GENERAL is not a verified path to an executive. No email prediction, restricted-site scraping, access bypass, automated LinkedIn actions or personal-number harvesting.

DIRECT_HIRING can preserve a current official ATS application as MANUAL_APPLICATION_POSSIBLE_OWNER_AUTH_REQUIRED without a named hiring manager. An application and a direct message are separate external actions, neither authorized by a research assessment. If person route/history is unknown, label NO_VERIFIED_PERSON_ROUTE or PRIVATE_HISTORY_UNAVAILABLE and do not promote contact readiness.

## Bounded professional contact-finding procedure

For every specifically selected leader, follow this order, stopping when a grounded route is found or the accessible public sources are exhausted:

1. Check the **current employer's official** leadership/staff/contact directory or individual biography for a **named** work email, named office line, or person-specific public booking/contact page. Quote the source's person-to-contact association; an employer's generic number is not that person's phone.
2. Check publicly accessible, dated event/speaker pages, industry-association bios, and official professional publications for a contact expressly associated with that same person. Resolve employer and identity conflicts before accepting a historical contact. Prefer the current employer's route over old affiliations.
3. Check an identifiable individual LinkedIn/professional profile as a **profile reference**, not proof that a message can be delivered or that the person accepts invitations. Do not scrape or bypass sign-in, infer an email from naming conventions, or treat a public profile as a verified inbox.
4. If only company reception, generic press/HR inbox, or a general form is available, label **INDIRECT_GENERAL** and retain it as an indirect fallback, never a verified person-specific route. If nothing is found, use **NO_VERIFIED_PERSON_ROUTE** with the failed searches and a concrete follow-up task.

For the human-facing private research brief record: **contact type** (LISTED_WORK_EMAIL / LISTED_OFFICE_PHONE / VERIFIED_PERSON_SPECIFIC_FORM / INDIVIDUAL_PROFILE_IDENTIFIED / INDIRECT_GENERAL / NONE), exact **publicly listed professional value** (or NOT_FOUND), supporting source URL, source publisher, source date/UNDATED, check date, and whether that source actually binds the contact to the selected person and current employer. A direct work email or office phone must be explicitly published in a professional context; do not harvest private/mobile numbers or personal email addresses. Never convert an aggregator's unverified address or an inferred pattern into a DIRECT route.

V2.2 `executive.route` remains a minimal structural research field; the human-facing contact summary may include sourced work email/phone not represented by that field. A route URL, `verified_for_person` flag or self-reported `page_read_success` never independently proves reachability. Record unknowns honestly. A published contact finding is not CONTACT_READY, and it is not an authorization to communicate. Keep public professional contact details out of PUBLIC Git and all personal communications behind separate human approval.

## Output boundary

Return only cited facts, clearly marked hypotheses and reason-coded HOLDs. Record whether this specialist was natively selected, NOT_VERIFIED, or SKIPPED_NOT_APPLICABLE. Research findings and drafts are not contact-ready or sent.

## V2.2 candidate hardening — supervised opt-in only

Read `../../../references/career-intelligence-operating-contract-v2.2.md` and `../../../docs/CAREER_V22_MASTERING_GATES.md` only when explicitly running the V2.2 pilot. V2.2 distinguishes PROFILE_IDENTIFIED from VERIFIED MANUAL PERSON ROUTE and VERIFIED WARM INTRO. A media inbox or general company line is indirect only; messaging permissions, identity, history and opt-out remain independently unresolved until checked. Native activation and source truth require independent proof. Neither a skill text read nor this instruction grants contact, drafting, sending, applications, private-memory access, or production authority.
