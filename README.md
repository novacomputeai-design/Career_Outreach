# Personal Executive Outreach Intelligence Agent

A Tucson-first, industry-agnostic, daily executive-networking research system. **Target: 20 newly qualified, contact-ready people per calendar day**; never manufacture prospects to fill the target. Suitable remote opportunities are also in scope.

**Status: v0.1 foundation — skills, operating contracts, deterministic qualification, and tests. Not yet connected to a live autonomous web-research provider or private relationship store.**

## Purpose
Identify relevant organizational leaders, actual or potential hiring influencers, and strategic connectors for thoughtful professional conversations. This is a personal career/networking workflow, **not** Nova Compute business sales and **not** an automated application or bulk outreach bot.

## Repository structure
- `AGENTS.md` — authority and repo rules.
- `.agents/skills/` — native repository-local Agent Skills, including the daily orchestration skill.
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

## Start
1. Open this repository in Codex; Codex loads local skills from `.agents/skills/`.
2. Invoke `$daily-executive-outreach` (or request the agent to run the daily executive networking workflow).
3. Provide authorized research capability and a private persistence layer. Skills are instructions, **not schedulers or web connectors**.
4. Evaluate with `python scripts/validate_project.py` and `python -m unittest discover -s tests -v`.

## Deployment milestones
- **Phase A (implemented foundation):** skill contracts, qualification policy, sample daily brief, evaluation and tests.
- **Phase B (not yet implemented):** approved web-research runtime with source adapters and secure local/private contact store.
- **Phase C (not yet implemented):** real-world pilot, audited 20-per-day target, calibrated rankings, human-reviewed messages.
- **Phase D (not yet implemented):** daily scheduler, operational monitoring, alerting and recovery after Phase C passes.

See `references/daily-operating-contract.md` for the detailed workflow.
