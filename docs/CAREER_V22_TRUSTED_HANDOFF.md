# Career V2.2 — Trusted Operator Handoff (DRAFT)

This is a staged research-only bridge from Codex live research to owner-controlled public-text evidence, existing read-only protected relationship memory, and owner-session-bound preference events. It has **no contact-ready, sending, application or scheduling authorization**.

## Trust boundary

Codex may create a V2.2 JSON research packet but must never run the owner wrapper. The wrapper is for the owner's normal interactive Windows PowerShell only; it unlocks the existing user-DPAPI state/identity keys, checks the current database read-only and clears environment secrets. Neither the keys, the history nor the private decision journal belong in Git or Codex.

An owner-run source witness:
- accepts only operator-allowlisted exact HTTPS public hostnames;
- disallows redirects, non-public DNS answers, unexpected ports, inherited proxy settings and unbounded fetches; pins the TLS socket using curl --resolve to a public DNS answer verified within the fetch; checks normal hostname and certificate validation (no --insecure);
- checks independently retrieved webpage text for exact source excerpts;
- HMAC-binds the receipt to the exact research packet using the owner-private identity key;
- **does not** establish semantic truth of an executive role, legal transaction, vacancy, or program ownership.

An owner decision is an interactive **research preference**, bound to the exact assessor report, witness digest, specific opportunity, reason, local novelty status and previous signed journal event. The journal does not establish independent biometric identity or external conversation history. Deleted valid journal tails require a future off-device trusted anchor to detect. Current SEND_AUTHORIZED remains blocked.

## Supervised operator sequence

### A. Codex research (untrusted)

In the V2.2 hardening branch, launch Codex normally, choose the daily-executive-outreach skill using the native picker, and direct it to the V2.2 contract. Have it save a strict V2.2 JSON packet to a private file outside the Git checkout, such as:

%LOCALAPPDATA%\CareerOutreach\runs\pilot-research.json

No private memory, DPAPI, owner decisions, outreach or applications in Codex. Skill activation is NOT_VERIFIED unless supported by actual host events.

### B. Structural evaluator (no protected keys)

From PowerShell in the repository, run:

python scripts/assess_career_opportunities_v22.py --input "$env:LOCALAPPDATA\CareerOutreach\runs\pilot-research.json" --out "$env:LOCALAPPDATA\CareerOutreach\runs\pilot-assessed.json" --history-dir "$env:LOCALAPPDATA\CareerOutreach\opportunities-v22"

Use a new output filename for every non-idempotent run. The JSON packet remains source-reported. The evaluator never certifies a real contact or an employer hiring need.

### C. Independent bounded source-text witness (OWNER ONLY)

Manually inspect the packet source URLs, then choose the exact hostname allowlist. For example:

pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode SourceWitness -Packet "$env:LOCALAPPDATA\CareerOutreach\runs\pilot-research.json" -Out "$env:LOCALAPPDATA\CareerOutreach\runs\pilot-witness.json" -AllowHost @("www.bannerhealth.com","www.tep.com")

The owner types a run-specific FETCH challenge, then a keyed source receipt is saved. A page hosting a stale biography may still match its text; that alone never proves current affiliation. Failures result in HOST_NOT_APPROVED, FETCH_UNAVAILABLE or TEXT_NOT_FOUND rather than fabricated verification.

### D. Owner history check and preference (OWNER ONLY)

Read the assessed report and source receipt first. Choose the appropriate result index. For example:

pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode OwnerReview -Report "$env:LOCALAPPDATA\CareerOutreach\runs\pilot-assessed.json" -Witness "$env:LOCALAPPDATA\CareerOutreach\runs\pilot-witness.json" -Index 0 -Decision RESEARCH_MORE -Reason SOURCE_GAP

This process checks the existing private relationship store read-only. It displays the proposed internal responsibility and requires typing a REVIEW challenge tied to the report hash. A HMAC-chained, research-only owner preference is appended outside Git. PURSUE is not an instruction to send.

### E. Verify local integrity and learn (OWNER ONLY)

pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode VerifyJournal

pwsh -NoProfile -File .\scripts\owner-career-v22.ps1 -Mode LearningProposals

Only research suggestions emerge. No policy weights change automatically.

## Scope of proof

| Stage | Evidence | Not proven |
|---|---|---|
| Codex research | source packet and host transcript if captured | native specialist invocation without host-side proof |
| Offline preflight | schema, record identity, contribution and timing structure | live source truth or hiring gap |
| Owner source witness | public text reproduced on bounded fetched webpage; receipt HMAC | truth of publisher claims, stale title resolution, semantic accuracy |
| Owner history check | local encrypted records read with existing DPAPI keys | outside-email/LinkedIn novelty or reachability |
| Owner decision | explicit interactive review and keyed journal integrity | hardware-verified human identity or external contact consent |
| Operational safety | zero outbound actions in these modules | production authorization |

## Remaining mandatory release gates

- Native skill invocation observed through the supported Codex host mechanism.
- Independent higher-assurance source truth (stale executive biography conflicts, JS ATS sources and sourced program ownership).
- Hardware/independently authenticated operator identity and a trusted off-device journal checkpoint, if required for production-grade approvals.
- Full cross-channel relationship and professional route reconciliation; local absence is never verified novelty.
- Real owner Windows read-only field rehearsal, negative tests, interruption recovery and 54-case adverse host results, followed by P4/P5 criteria.

The current engineering branch is **not production-qualified**. Do not run these commands from Codex, a scheduled unattended session, or an untrusted process. No protected database migration is required or authorized.

## Network isolation and operator prerequisites

The witness requires a functioning local curl executable with --resolve support. The original requests.get implementation permitted DNS validation followed by a separately resolved connection (DNS rebinding); the current fetch rejects mixed public/private DNS records and pins the real HTTPS socket to the checked address. Missing curl, invalid certificates, redirect status or source-rendering restrictions => FETCH_UNAVAILABLE, not an unpinned fallback. This is a defense-in-depth boundary, **not** equivalent to operating-system network sandboxing; owner-controlled network egress isolation is required for a higher-assurance production source verifier.

Before any real owner-Windows exercise, test on a dedicated restored or synthetic environment. An owner's existing DPAPI database is not a test fixture; do not run Codex with owner keys present in its process environment. The private folder and signed research journal are not cryptographically isolated from other programs running under the same Windows user account. Actual role/owner truth must still be checked against independent current evidence.
