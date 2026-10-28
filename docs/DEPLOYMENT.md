# Deployment: Codex-native is the primary path

Start with [Codex-native activation guide](CODEX_NATIVE_RUN.md). Codex CLI using ChatGPT sign-in is selected as the agent, the 14 skills are local, and no Tavily/OpenAI API credentials are required for this selected path. Actual live web availability and skill invocation still need proof.

The older `python -m outreach_agent run` implementation described below is OPTIONAL and separately requires Tavily/OpenAI API keys. Its Windows Task Scheduler/cron examples do not run the Codex-native skill workflow.

## Optional provider-backed Python deployment

This is a PUBLIC GitHub repository. Private keys, history, daily reports, approved drafts and personal correspondence must remain on a separate protected machine or database outside the checkout.

## Prerequisites
- Trusted persistent Windows or Linux host; Python 3.11 or newer; install dependencies with: python -m pip install -r requirements.txt.
- TAVILY_API_KEY (Tavily web search) and OPENAI_API_KEY (evidence extraction). API consumption may incur charges. Neither is provided by this repo.
- OUTREACH_DB_PATH must point to private storage outside repository.
- OUTREACH_STATE_KEY is a stable Fernet encryption key; generate ONCE using Python: from cryptography.fernet import Fernet; print(Fernet.generate_key().decode()).
- OUTREACH_IDENTITY_KEY is a separate stable HMAC key; generate ONCE: import secrets; print(secrets.token_hex(32)).
- Keep keys in a user secret manager, not .env checked into Git. Protect the backing drive and back up keys+database securely.

## Local pilot
python -m outreach_agent run --out /path/outside/repo/report.json --target 5 --max-queries 4

Independent human review is required before calling recommendations fully verified or reachability proven. This implementation does not access or automate LinkedIn.

## Relationship observations and learning
After personally sending an approved introduction, record an actual CONTACTED event for that person using:
python -m outreach_agent record --person-id ID --event CONTACTED
When the person actually replies: use --event REPLIED.
For an observed meeting, introduction or opportunity: use MEETING, INTRODUCTION or OPPORTUNITY.
For someone declining: use OPTED_OUT. These events are not inferred from search results.
Separate draft content approval and permission to send are recorded with:
python -m outreach_agent approve --person-id ID --draft-file /private/draft.txt --stage CONTENT_APPROVED
# SEND_AUTHORIZED is intentionally BLOCKED until recipient, route, history and operator authorization are qualified.
# Do not attempt or automate this transition.
The CONTENT_APPROVED command never sends a message. Its record is not dispatch authorization.
Review descriptive feedback via: python -m outreach_agent learning
After reviewing the sample sizes and tradeoffs, explicitly prioritize one geographic discovery query family with:
python -m outreach_agent approve-strategy --segment remote
This changes QUERY ORDER only, not eligibility or evidence thresholds.

## Daily schedule
On Windows, inspect deploy/windows-task.ps1. On Linux, adapt deploy/cron.example. Install only after a successful authorized live pilot and confirm the scheduler's execution-account secrets persist. GitHub Actions CI is deliberately NOT configured to perform secret-bearing live research or export private people.

## Qualification gate
The following remain operational requirements, not proven by installing packages: seven real daily runs, native host skill activation, source verification accuracy, >=40 independently assessed people, personal usefulness feedback, suppression correctness, safe recoverability and zero unauthorized sends. A CI pass or exact-quote match alone is NOT independent production qualification.


## Recover after an output-file crash
The completed full report is stored encrypted inside the private database before it is written to an external file. Recovery:
python -m outreach_agent restore-report --out /private/restored-report.json
Do not rerun a failed-to-export successful run just to replenish the quota; doing so properly flags already stored identities as duplicates.

## Provenance and freshness limitations
Actual role verification still requires expert review of first-party current pages. Two distinct hosts and verbatim excerpts are corroboration signals, not proof of hiring authority or current engagement. An explicitly published source older than two years is not accepted as current role evidence. Undated sources remain freshness-unknown.


## Mandatory budgets and user source review
The research runtime limits calls per run (default 50 Tavily searches and 40 model extraction requests). Override with --max-search-calls and --max-extractions only after reviewing pricing and logs. The person-level record is SOURCE-CORROBORATED, not automatically production-verified.
After checking current role and organization, the contact route's true reachability and the personal relevance yourself, mark a candidate:
python -m outreach_agent review-contact --person-id ID --confirm-current-role --confirm-contact-route --confirm-professional-relevance
This does not send anything; it simply registers human validation. A general contact page is INDIRECT and may not reach the executive.
