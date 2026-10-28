# Personal Executive Outreach Intelligence Agent

A Tucson-first, industry-agnostic, daily executive-networking research system. **Target: 20 newly qualified, contact-ready people per calendar day**; never manufacture prospects to fill the target. Suitable remote opportunities are also in scope.

**Status: Codex-primary with Memory and Governance prioritized as early production gates (NOT production-qualified).** Codex authentication, supervised research, private owner-PowerShell relationship checks and offline tests have been observed. Specialist activation, safe automatic reconciliation and runtime governance enforcement remain open. [Production plan](docs/PRODUCTION_PLAN.md).

## Purpose
Identify relevant organizational leaders, actual or potential hiring influencers, and strategic connectors for thoughtful professional conversations. This is a personal career/networking workflow, **not** Nova Compute business sales and **not** an automated application or bulk outreach bot.

## Repository structure
- `AGENTS.md` — authority and repo rules.
- `.agents/skills/` — 14 repository-local Agent Skills, including the daily orchestration and learning skills.
- `config/` — **public-safe** professional positioning and targets.
- `references/` — evidence, scoring, handoffs, state machine, privacy and source policies.
- `evals/` — adversarial acceptance cases.
- `scripts/` — deterministic checks and local sample brief generation.
- `.github/workflows/` — CI for validation; live outreach automation is **not** enabled by CI.

## Mandatory constraints
1. Candidate must have a **verified full name, current leadership role, organization, source URLs, specific reason to connect, and legitimate public professional contact path** to count toward the 20.
2. Tucson first, remote acceptable, **all industries** considered when demonstrably aligned with experience.
3. Never guess a person's email, scrape restricted sites, bypass access controls, mass-send messages, or publish private relationship history.
4. **Explicit user approval for each outbound message and separate authorization for sending.** Draft approval alone is not send permission.
5. The GitHub repository is **public**. Never commit personal phone numbers, private emails, CRM records, contact history, credentials, or copied resume documents.
6. Preserve state and deduplicate by stable contact identity before ranking or reporting. Distinguish verified facts from hypotheses.
7. Each report identifies sourcing gaps, skips and shortfalls; no fabricated contacts or urgency.
8. Do not conflate career networking with outreach on behalf of Nova Compute AI.

## Start — Codex-native path
Read [Codex-native activation guide](docs/CODEX_NATIVE_RUN.md) before starting live research. The first run is read-only and must prove actual skill selection.

1. Open this repository in Codex; confirm local skills from `.agents/skills/` are available.
2. Invoke `$daily-executive-outreach` (or request the agent to run the daily executive networking workflow).
3. Provide authorized research capability and a private persistence layer. Skills are instructions, **not schedulers or web connectors**.
4. Evaluate with `python scripts/validate_project.py` and `python -m unittest discover -s tests -v`.

## Production plan — mandatory sequence

1. **P0: Governance policy baseline** — one versioned machine policy, consistent skills/docs and drift regression tests.
2. **P1–P2: Protected relationship memory** — recovery and controlled owner-context batch reconciliation; do not bypass Codex sandbox DPAPI boundary. See [operator batch proof](docs/OPERATOR_BATCH_SCREENING.md) (not yet Windows-qualified).
3. **P3: Deterministic governance enforcement** — initial review and content-approval preconditions plus encrypted audit implemented. **`SEND_AUTHORIZED` is now blocked by code** until independently qualified recipient/route/relationship-history proof and trusted human authorization exist. No sender is integrated.
4. **P4: Real supervised Codex end-to-end pilot** — research, trusted memory, evidence and qualified human review.
5. **P5: Production qualification** — seven real daily runs, >=40 independently assessed contacts and operating reliability checks.

Machine-readable authority: [config/operating-policy.json](config/operating-policy.json). See [production plan](docs/PRODUCTION_PLAN.md) and [current gap closure](docs/GAP_CLOSURE_MATRIX.md). No automatic sending.

## Optional Tavily/OpenAI Python runner (NOT the selected Codex architecture)

The following `python -m outreach_agent run` command still requires both provider API keys. This is a fallback implementation; do not use it as proof of Codex-native skill invocation.

## Executable pilot commands

Read [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for environment/secret requirements, supported daily schedule recipes and genuine-outcome feedback commands. From a persistent host after installing requirements and protecting the private database/keys:

- python -m outreach_agent run --out /private/daily.json --target 5 --max-queries 4
- python -m outreach_agent learning
- python -m unittest discover -s tests -v

No external messages are sent by this code, ever. The daily run's source-corroboration checks are conservative but not a substitute for user review or independent live evaluation. Reports and relationships must remain off this public repository.

### Pilot evidence-count semantics

`source_corroborated_pending_human_review` is the output of automated research and source checks. **It is NOT the number of contact-ready people.** The `new_contact_ready` and `production_verified_contact_ready` counters remain zero until a separately recorded and auditable independent review is complete. Never interpret a passing GitHub CI run or the research target being met as authorization to contact anyone.

After independent human verification of a particular record, `python -m outreach_agent review-contact --person-id ID --confirm-current-role --confirm-contact-route --confirm-professional-relevance` records that fact in the private store. `python -m outreach_agent run-readiness --run-id RUN-ID` now reports only **recorded source/route/fit reviews**. Until the protected cross-channel history and independently verified CONTACT_READY gate exist, it explicitly reports **0 production-verified contact-ready**. Neither command sends outreach, authenticates the reviewer, or proves novelty.
