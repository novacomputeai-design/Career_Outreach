---
name: contact-verification
description: Verify each prospective leader's current identity, role, organization and a permitted professional contact route using traceable, dated evidence.
---
# contact-verification

Read `../../../references/source-and-contact-policy.md`. Resolve namesakes, dated bios and employer changes; prefer current first-party evidence. Capture URL, observed date, claim supported and any discrepancy. Obtain a legitimately public professional contact path: published business contact, official indirect form, permitted event/association introduction or manually used platform link. Label DIRECT, INDIRECT or MANUAL; a form is not a personal address. NEVER infer email addresses or automate LinkedIn scraping/sending. Mark VERIFIED only when all material claims and a route are supported, otherwise HOLD with reason. Preserve source-level confidence.

## Selected-person professional route verification

For each selected PRIMARY and justified ALTERNATE from leadership-discovery, perform a bounded **person-specific** source check: (1) current employer individual staff/office/contact pages; (2) accessible professional event, industry association, author/speaker publications; and (3) appropriate lawfully public institutional sources when relevant. Inspect one promising source for name/employer binding, publication age and intended contact purpose. Record the lanes attempted and their negative results or reason for early stop. For a supported recruiter/role promoter, look for a recruiting-process route suitable for inquiries about the **exact vacancy**, not an unrelated personal or procurement contact. Never infer or harvest email patterns or private/mobile numbers, scrape gated sites, bypass platform controls or automate outreach.

Keep these **research-only** classifications separate:
- `CURRENT_PERSON_WORK_ROUTE`: currently published name-bound suitable professional email, dedicated office number or individual form; public listing is not proof of delivery or consent.
- `HISTORICAL_PERSON_WORK_CONTACT_RECHECK` / `PURPOSE_RESTRICTED_ROUTE_REVIEW`: older named conference email or an address provided for media/procurement/legal use; not automatically a current career route.
- `ROLE_SPECIFIC_PROMOTION_ONLY`: a person posted/shared the exact role and said **"apply today"** or equivalent, without actually inviting the reader to contact them personally.
- `ROLE_SPECIFIC_INVITATION_PUBLIC`: a source-verified first-person invitation such as **"contact me about this role"**; this is a reason-to-connect signal, **not a verified messaging channel** or permission to automate.
- `PROFILE_ONLY`: current individual professional profile without proved reachability. `INDIRECT_GENERAL`: generic company/HR contact, not a named person's route. `OFFICIAL_APPLICATION_ROUTE`: verified employer job-application channel, separate from contacting any executive.

When no present, appropriate person-bound professional channel is verified, explicitly return `CONTACT_HOLD` and a concise source-lane trail; preserve any role-specific reason to inquire. Apply the existing novelty, owner review, and no-send gates independently. Fixed-employer tests must not expand to unrelated employers after a route HOLD.

