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

## Safe next operator step (synthetic only)

Before any DPAPI owner-session operation, switch to the V2.2 draft branch in a normal PowerShell window, verify that the working tree is clean, and run:

    .\scripts\career-v22-synthetic-only.ps1

This runner refuses an incorrect branch or owner state/identity secrets in environment. It exercises only synthetic tests, using generated test keys and temporary databases. It does not read any live DPAPI file or relationships.sqlite, browse real sites, invoke Codex or authorize contact. The pinned curl client is started with --disable as the first option, ignoring potentially unsafe user curl configuration. A local PASS does not satisfy the live independent Codex, operator Windows DPAPI, or source-semantic release gates.

## Host-native skill activation diagnostic (operator-run, no computer-use UI)

The Codex tool interface used from another service may not expose the local native skill picker. This is **not evidence** that the locally installed Codex CLI cannot discover the skills. OpenAI's documented skill evaluation approach uses explicit `$skill-name` invocation, `/skills` in interactive sessions, and `codex exec --json` to capture host events. Event logs are evidence to inspect, not a skill attestation by themselves.

From a clean checkout on the V2.2 draft branch, with no private relationship keys in environment, run in a **normal operator PowerShell terminal**:

    .\\scripts\\career-v22-native-skill-probe.ps1

The script invokes `codex exec --json --sandbox read-only` on a **skills-discovery-only** prompt and saves stdout JSONL and stderr in a uniquely named local TEMP directory. It neither reads private memory nor carries approval authority. Do not run through a computer-use approval request. No full-auto or workspace write permission is provided. Keep raw event logs private, review/redact before sharing, and report **NATIVE_SKILL_INVOCATION=NOT_VERIFIED** unless actual native host evidence exists. Model claims, self-generated trace files, reading SKILL.md, and zero exit code never count as such evidence.

A separate regression now allows an explicitly referenced, source-reported conflicting current-role claim to raise SOURCE_CONFLICT, even without the exact EXECUTIVE_AFFILIATION_ENDED label, as long as it links the correct person, employer, and current-role claim ID. Unstructured contradictory prose must be normalized by a human/researcher with supporting source evidence; arbitrary text matching is not sufficient to establish departure.

## Unrelated Notion OAuth startup failure during native skill probe

On Windows, if the optional configured Notion MCP server reports `AuthRequired` and PowerShell prints a `node.exe` error record, this is **not** evidence about Career Outreach skill activation. The native-skill probe explicitly adds a **per-command** Codex setting `-c 'mcp_servers.notion.enabled=false'`; it does not edit `~/.codex/config.toml`, authorize Notion or alter other MCP servers. The script also scopes PowerShell `ErrorActionPreference=Continue` around native Codex execution to capture stderr and report exit status, then restores strict handling. This prevents an unrelated native stderr warning from suppressing the diagnostic summary. The expected outcome remains `NATIVE_SKILL_INVOCATION=NOT_INDEPENDENTLY_VERIFIED_BY_THIS_SCRIPT` until raw host evidence is reviewed. If the MCP server is configured under a different ID or a required server fails, do not disable arbitrary integrations: inspect the local stderr log and report HOLD.
