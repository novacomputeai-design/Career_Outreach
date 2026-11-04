# Leader and professional contact discovery — human-facing brief contract

**Purpose:** A compact read-only Codex shortlist of the best people to contact
about the owner's *personal* AI strategy/transformation or enterprise product
leadership career goals. This is NOT a new agent, database schema, application
or sending workflow. Existing V2.1/V2.2 safety and source-truth limits govern.

## One result per useful leader

For each organization, report:
- **Organization and work feasibility:** Tucson/Southern Arizona first, genuinely feasible US-remote next; industry agnostic.
- **Why now:** one concrete, dated business initiative / product change / official job with an exact visited source. Distinguish observed employer claim, inferred opportunity, and confirmed opening.
- **Primary leader:** current full name, exact employer and title, separately sourced current-role evidence; resolve departures and namesake confusion.
- **Why this leader:** DOCUMENTED link to the business outcome or initiative, or clearly marked FUNCTIONALLY_PLAUSIBLE. Explain decision influence and why this person is more appropriate/accessible than the CEO. Give up to one evidence-supported alternate, not a second generic executive.
- **Why this candidate:** one bounded responsibility related to the approved public résumé, a concrete value hypothesis, and limitations. Hiring interest must not be inferred from AI mentions.
- **Professional contact:** type, exact public work contact value *if listed*, publisher and source URL, last checked date, contact-to-person linkage and any accessibility caveat. Use NOT_FOUND rather than guessed or personal details.
- **Next manual step:** e.g. inspect official directory, check a newer role source, request owner review of a sourced contact. No unsolicited sending or automatic application.

## Contact types and report-only result buckets

| Contact type | Evidence required | Brief bucket |
| --- | --- | --- |
| LISTED_WORK_EMAIL | Source expressly pairs named current professional with their published employer/work address | PERSON_ROUTE_SUPPORTED |
| LISTED_OFFICE_PHONE | Official/current source expressly pairs named person with an office number; not main switchboard | PERSON_ROUTE_SUPPORTED |
| VERIFIED_PERSON_SPECIFIC_FORM | Official permitted public professional form that targets named person, source-linked | PERSON_ROUTE_SUPPORTED |
| INDIVIDUAL_PROFILE_IDENTIFIED | Identity-checked profile; messaging reachability/permission NOT established | PROFILE_ONLY |
| INDIRECT_GENERAL | General company line, HR/press inbox or generic contact form only | CONTACT_HOLD |
| NONE | No trustworthy, current person-specific route | CONTACT_HOLD |

A published work contact is source **listed**, not independently confirmed to
deliver a message. A person-specific source contact does not establish an
existing relationship, acceptance of contact, hiring interest, or readiness
to send. These three buckets are HUMAN-FACING FINDING labels only and MUST
NOT replace `research_state`, `engagement_readiness`, `contact_ready`,
`send_authorized`, or protected owner history.

## Brief presentation

A compact table may summarize:
`Organization | Why now (source) | Leader/title (role source) | Why this leader | Work contact/type (source, checked) | Bucket | Next step`.

For a leadership-hiring route with a current official ATS but no safe person,
retain that official opening in a separate employer-opportunity backlog with
`EXECUTIVE_OWNER_UNVERIFIED` and **no invented hiring manager**. Do not
count it as a verified person contact.

Totals should differentiate investigated organizations, current named
leaders, DOCUMENTED vs FUNCTIONALLY_PLAUSIBLE responsibility, sourced
person-specific contact values, profile-only, and contact holds. It is fine
to return fewer than the requested count.

## Working with the V2.2 packet schema

The existing strict research **input** schema has
`executive.route = {route_type, verified_for_person, url}`; it does not
store an email address or telephone number. Do not silently jam contact
values into the `url` field or expand the schema without a separate,
tested change. The human-facing report may present published professional
email/phone as a **sourced display-only contact finding**, saved to the
owner-approved private research output, outside PUBLIC Git.

When a DIRECT route has evidence, `executive.route.url` refers to its
public HTTPS source/official route page, and only the human-facing brief
shows the listed email/office phone. A mere URL to a generic bio/contact
page cannot set `verified_for_person=true`. An identified LinkedIn URL
is at most PROFILE_ONLY until a permitted person-specific messaging route
is actually established. No automated LinkedIn interaction or scraping.

**Always:** no invented addresses, scraped personal numbers, private emails,
credential bypass, false current-affiliation claims, contacts in PUBLIC Git,
DPAPI access from Codex, drafting without request, sending or applications.
Native skill activation remains NOT_VERIFIED absent independent host proof.
