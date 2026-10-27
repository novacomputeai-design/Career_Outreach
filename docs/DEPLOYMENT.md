# Deployment: manual authorization and external services required

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
python -m outreach_agent approve --person-id ID --draft-file /private/draft.txt --stage SEND_AUTHORIZED
These commands NEVER send messages or invite contacts.
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
