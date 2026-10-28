# Production evidence and gap closure — 2026-10-28

Authority: `config/operating-policy.json` v0.2.0 and `docs/PRODUCTION_PLAN.md`. Written instructions and successful CI do NOT prove live runtime policy enforcement.

| Capability | Observed baseline | Open requirement |
|---|---|---|
| Codex | CLI v0.164.0 authenticated using ChatGPT; primary skill invocation reported | Specialist native invocation NOT VERIFIED |
| Live research | Supervised five-person Codex web pilot; two provisional, three held, 0 new contact-ready | Source/route review and full skill integration |
| Private memory | Encrypted SQLite + HMAC identity; owner-shell DPAPI; classifications persisted; offline tests | Reliable batch match, recovery, retention and alias handling |
| Automatic Codex memory | User tried same DPAPI wrapper inside sandbox | **BLOCKED:** Windows DPAPI decrypt failure; keep sandbox and keys protected |
| Operator protected batch screening | Bounded owner-context batch code, read-only SQLite, synthetic tests added | Real Windows user run and governed handoff NOT YET VERIFIED; **not** a Codex automatic broker |
| Governance | Versioned rules, opt-outs, separate draft-content and send-authorization records | Hard deterministic runtime gates and policy-versioned audit **NOT END-TO-END** |
| Daily reports | Honest shortfall counts in optional Python runner | Codex-native reconciled private brief, source review and human approvals |
| Scheduling | OPTIONAL Tavily/OpenAI Python scheduler examples only | Codex-native monitoring/scheduling and recovery unqualified |
| Field qualification | Offline tests passed | 7 real daily runs, >=40 independently reviewed real people, 0 unauthorized actions |

The Tavily/OpenAI-key research runner is **optional legacy**, not the selected Codex workflow. Do not prompt for API keys for Codex-native operation. **Do not run the DPAPI wrapper inside Codex or bypass its sandbox.**

Critical path P0 → P1/P2 → P3 → P4 → P5 is defined in `docs/PRODUCTION_PLAN.md`. Issues #1 #2 #3 #9 remain open; do not claim production readiness.
