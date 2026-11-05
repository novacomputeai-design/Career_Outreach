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

For each prioritized employer's primary leader (and a supported alternate where justified), perform the following bounded search in depth. Do not stop just because an individual profile was found; check relevant official and professional sources for an actual person-specific work route. Stop only when a source-supported person-specific route is established or the accessible source paths below have been checked, recording which were tried:

1. Check the **current employer's official** leadership/staff/contact directory or individual biography for a **named** work email, named office line, or person-specific public booking/contact page. Quote the source's person-to-contact association; an employer's generic number is not that person's phone.
2. Check publicly accessible, dated event/speaker pages, industry-association bios, and official professional publications for a contact expressly associated with that same person. Resolve employer and identity conflicts before accepting a historical contact. Prefer the current employer's route over old affiliations.
3. Check an identifiable individual LinkedIn/professional profile as a **profile reference**, not proof that a message can be delivered or that the person accepts invitations. Do not scrape or bypass sign-in, infer an email from naming conventions, or treat a public profile as a verified inbox.
4. If only company reception, generic press/HR inbox, or a general form is available, label **INDIRECT_GENERAL** and retain it as an indirect fallback, never a verified person-specific route. If nothing is found, use **NO_VERIFIED_PERSON_ROUTE** with the failed searches and a concrete follow-up task.

For the human-facing private research brief record: **contact type** (LISTED_WORK_EMAIL / LISTED_OFFICE_PHONE / VERIFIED_PERSON_SPECIFIC_FORM / INDIVIDUAL_PROFILE_IDENTIFIED / INDIRECT_GENERAL / NONE), exact **publicly listed professional value** (or NOT_FOUND), supporting source URL, source publisher, source date/UNDATED, check date, and whether that source actually binds the contact to the selected person and current employer. A direct work email or office phone must be explicitly published in a professional context; do not harvest private/mobile numbers or personal email addresses. Never convert an aggregator's unverified address or an inferred pattern into a DIRECT route.

V2.2 `executive.route` remains a minimal structural research field; the human-facing contact summary may include sourced work email/phone not represented by that field. A route URL, `verified_for_person` flag or self-reported `page_read_success` never independently proves reachability. Record unknowns honestly. A published contact finding is not CONTACT_READY, and it is not an authorization to communicate. Keep public professional contact details out of PUBLIC Git and all personal communications behind separate human approval.

## Contact-search depth, age and intended-use checks

For each selected primary leader and any supported alternate, perform **at least three distinct public-source lanes when available** before declaring NO_VERIFIED_PERSON_ROUTE, unless a current, suitable, named professional route is already found. Record the specific lanes searched, exact search/source URL, and negative result or reason for stopping. Lanes:

- **Official employer:** staff/leadership directories, role biography, contact pages, and indexed official pages using exact-name + employer/domain queries.
- **Professional appearances:** conferences, speakers, association rosters, public publications, interviews and current professional biographies.
- **Public institutional records:** indexed, lawfully public government/utility documents, procurement and contract PDFs, agency directories and publicly filed professional documents, using exact person+employer queries. Use these only as evidence of *historically published professional identity/contact*; do not treat contract-administration or bid-only details as a general-purpose networking route.
- **Identity/profile fallback:** verify individual public professional profile identity and current affiliation without scraping, automated platform actions, sign-in circumvention or inferred contact details.

Classify every discovered contact independently by **identity match**, **currentness**, and **intended purpose**:
- `CURRENT_PERSON_WORK_ROUTE` only when the source ties the exact person to a work email, dedicated office number, or person-targeted form and there is no material freshness/purpose contradiction. Public listing still does not prove delivery or consent.
- `HISTORICAL_PERSON_WORK_CONTACT_RECHECK` when the only evidence is an older contract, event or archived directory; show source/date but do **not** claim current reachability.
- `PURPOSE_RESTRICTED_ROUTE_REVIEW` when a business contact was published specifically for government procurement, contract administration, legal matters or media; it may not be appropriate for career networking even if the person is current.
- `PROFILE_ONLY`, `INDIRECT_GENERAL`, or `NO_VERIFIED_PERSON_ROUTE` otherwise.

A name in a PDF is not enough: verify the document pairs the same person, the employer, and the actual business contact; check a newer official source for role continuity. Never guess email patterns, harvest personal/home/mobile contact information, scrape gated platforms, or send anything. These are **report-only evidence labels**, not changes to V2.2 route schema or a license to contact.

## Bounded contact completion and onward selection

For each employer's best evidenced practical conversation candidate and at most one supported alternate, run the three distinct available public-source lanes above; cap the search at a bounded **one pass per lane and one targeted source recheck** for a promising lead, not repeated open-ended variants of the same query. Record the exact search strings/pages and each result or access limitation. Stop early for a *current, suitable, person-specific professional route*; otherwise set `CONTACT_SEARCH_COMPLETED_NO_SUITABLE_ROUTE` after the lanes are exhausted, alongside the original contact classification and the one highest-value unresolved check. This is **not** a claim that no contact exists elsewhere.

When the practical candidate lacks a suitable route, test a source-supported alternate only if that alternate has real proximity to the same business decision; do not switch to a general switchboard or unrelated easier-to-contact executive. Once the bounded search is complete, **keep the employer as a research prospect and move on to the next already-screened qualified employer**. Do not discard the strategic signal, relax route standards, or spend the full run repeating generic email searches. A purpose-limited procurement contact is never promoted solely because a named address appears in an official PDF. No contact-ready or send authorization follows.

## Output boundary

Return only cited facts, clearly marked hypotheses and reason-coded HOLDs. Record whether this specialist was natively selected, NOT_VERIFIED, or SKIPPED_NOT_APPLICABLE. Research findings and drafts are not contact-ready or sent.

## V2.2 candidate hardening — supervised opt-in only

Read `../../../references/career-intelligence-operating-contract-v2.2.md` and `../../../docs/CAREER_V22_MASTERING_GATES.md` only when explicitly running the V2.2 pilot. V2.2 distinguishes PROFILE_IDENTIFIED from VERIFIED MANUAL PERSON ROUTE and VERIFIED WARM INTRO. A media inbox or general company line is indirect only; messaging permissions, identity, history and opt-out remain independently unresolved until checked. Native activation and source truth require independent proof. Neither a skill text read nor this instruction grants contact, drafting, sending, applications, private-memory access, or production authority.
