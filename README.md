# Personal Executive Outreach Intelligence Agent

A Tucson-first, industry-agnostic, daily executive-networking research system. **Target: 20 newly qualified, contact-ready people per calendar day**; never manufacture prospects to fill the target. Suitable remote opportunities are also in scope.

**Status: v0.2 executable pilot implementation — optional Tavily/OpenAI research adapters, source-excerpt checks, encrypted private SQLite store, approval-state separation, operator CLI, feedback metrics and scheduling recipes. Requires private API keys, real-world testing and a configured always-on host. NOT production-qualified.**

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

## Start
1. Open this repository in Codex; Codex loads local skills from `.agents/skills/`.
2. Invoke `$daily-executive-outreach` (or request the agent to run the daily executive networking workflow).
3. Provide authorized research capability and a private persistence layer. Skills are instructions, **not schedulers or web connectors**.
4. Evaluate with `python scripts/validate_project.py` and `python -m unittest discover -s tests -v`.

## Deployment milestones
- **Phase A (implemented foundation):** 14 skills, typed lead handoff, qualification policy, private store, and offline regression tests.
- **Phase B (code implemented, deployment NOT VERIFIED):** Tavily and OpenAI research adapters; locally encrypted private contact store. Needs API credentials and live independent testing.
- **Phase C (not yet implemented):** real-world pilot, audited 20-per-day target, calibrated rankings, human-reviewed messages.
- **Phase D (recipe available, NOT ACTIVATED):** Windows Task Scheduler and Linux cron examples; runtime monitoring/alerting and seven-day production qualification still pending.

See `references/daily-operating-contract.md` for the detailed workflow.

## Executable pilot commands

Read [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for environment/secret requirements, supported daily schedule recipes and genuine-outcome feedback commands. From a persistent host after installing requirements and protecting the private database/keys:

- python -m outreach_agent run --out /private/daily.json --target 5 --max-queries 4
- python -m outreach_agent learning
- python -m unittest discover -s tests -v

No external messages are sent by this code, ever. The daily run's source-corroboration checks are conservative but not a substitute for user review or independent live evaluation. Reports and relationships must remain off this public repository.

### Pilot evidence-count semantics

`source_corroborated_pending_human_review` is the output of automated research and source checks. **It is NOT the number of contact-ready people.** The `new_contact_ready` and `production_verified_contact_ready` counters remain zero until a separately recorded and auditable independent review is complete. Never interpret a passing GitHub CI run or the research target being met as authorization to contact anyone.
