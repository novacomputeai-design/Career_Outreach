> **V2.1 integration notice:** This section records the historical V1.1/legacy run state. The V2.1 candidate contract and `config/operating-policy.json > career_intelligence` control new research behavior. Legacy person scores and the 20-person daily figure are not V2.1 qualification criteria. All privacy, P0–P5 and no-send release gates remain in effect. Neither CI nor draft PR counts as a real native skill run.

# V1.1 organization-first implementation status

This is an **additive** career-opportunity precheck, not a second agent, automatic scheduler or a production qualification. Policy: config/operating-policy.json > opportunity_search. Source contract: references/opportunity-first-contract.md. Deterministic structural assessor: outreach_agent/opportunity_qualification.py.

The new module never opens a URL or asserts the published facts are true. It cannot authenticate owner-reported role discussions, the operator's identity, full private novelty or hiring authority. The optional older Tavily/OpenAI runner's original heuristic scoring is **legacy person fit only** and cannot be called V1.1 employer qualification.

The strict existing person-only Google CSV and operator DPAPI batch flow remain unchanged; no migration of SQLite, Drive rows, approval records or skills count. No secrets or actual private leads belong in GitHub. All potential candidates remain contact-ready=false, SEND_AUTHORIZED blocked.

## Validation
On Windows or the CI Windows/Ubuntu matrix run:
- python scripts/validate_project.py
- python scripts/validate_governance.py
- python scripts/check_public_repo.py
- python -m unittest discover -s tests -v

The synthetic V1.1 adversarial tests cover posted roles versus generic AI initiatives, private-owner attestation HOLD, exploratory hiring not confirmed, false CEO influence, generic forms, no route, infeasible credentials/geography, source freshness, score inflation, cross-project intent, O3/O4 exclusion, 3/2 allocation, parent concentration, shortfalls, and old-exporter compatibility.

## Field qualification still open
Independent current source truth, actual employer hiring need, named decision-maker and person-specific route, owner evaluation of the ten prior records and a five-opportunity pilot, native specialist activation and sustained P4/P5 reliability. Do not schedule autonomous discovery or send outbound contact.

## Field preflight finding — executive dependency decoupled
Real employer job postings often provide an application page but no named hiring manager. The initial V1.1 evaluator rejected these and could discard strong opportunities. The preflight patch now allows `ORGANIZATION_REVIEW_EXECUTIVE_PENDING` for O1 and public O2A with no individual and a zero person score. This remains entirely separate from personal novelty, route verification, contact readiness and sending authorization. Independently revisit actual employer postings: indexed jobs can be expired or absent on the primary board; a syntactically valid URL alone NEVER establishes a live vacancy.
