# Production evidence and gap closure — 2026-10-28

Authority: `config/operating-policy.json` v0.2.2 and `docs/PRODUCTION_PLAN.md`. Written instructions and successful CI do NOT prove live runtime policy enforcement.

| Capability | Observed baseline | Open requirement |
|---|---|---|
| Codex | CLI v0.164.0 authenticated using ChatGPT; primary skill invocation reported | Specialist native invocation NOT VERIFIED |
| Live research | Supervised five-person Codex web pilot; two provisional, three held, 0 new contact-ready | Source/route review and full skill integration |
| Private memory | Encrypted SQLite + HMAC identity; owner-shell DPAPI and batch passed on Windows; encrypted online snapshot/verify/restore-new coded | Owner Windows same-account encrypted recovery PASSED; portable key recovery beyond the Windows account, schema migration, retention and alias handling remain |
| Automatic Codex memory | User tried same DPAPI wrapper inside sandbox | **BLOCKED:** Windows DPAPI decrypt failure; keep sandbox and keys protected |
| Operator protected batch screening | Bounded owner-context batch code, read-only SQLite, synthetic tests added | Owner-Windows batch proof PASSED for three names; operator-controlled, **not** a Codex automatic broker |
| Personal career scope isolation | Scope is now asserted by policy ID and checked at candidate/review/report boundaries, with synthetic subcontracting cases | Human checks and live Codex agent activation still required; do not copy Nova subcontracting sources or targets into this repository |
| Career purpose isolation | Policy ID and explicit scope checks in candidate and review code, synthetic adversarial cases | Live Codex scope proof and human review unqualified |
| Governance | Versioned rules, opt-outs, separate draft-content and send-authorization records | First structural + operator-attested review + exact-draft approval guards with policy-versioned encrypted audit coded; human identity/provenance, trusted novelty, route-bound sending and full CONTACT_READY gate **NOT QUALIFIED**; SEND_AUTHORIZED now fails closed regardless of draft content approval |
| Daily reports | Honest shortfall counts in optional Python runner | Codex-native reconciled private brief, source review and human approvals |
| Scheduling | OPTIONAL Tavily/OpenAI Python scheduler examples only | Codex-native monitoring/scheduling and recovery unqualified |
| Field qualification | Offline tests passed | 7 real daily runs, >=40 independently reviewed real people, 0 unauthorized actions |

The Tavily/OpenAI-key research runner is **optional legacy**, not the selected Codex workflow. Do not prompt for API keys for Codex-native operation. **Do not run the DPAPI wrapper inside Codex or bypass its sandbox.**

Critical path P0 → P1/P2 → P3 → P4 → P5 is defined in `docs/PRODUCTION_PLAN.md`. Issues #1 #2 #3 #9 remain open; do not claim production readiness.
