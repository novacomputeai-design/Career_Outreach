> **V2.1 candidate branch:** Organization-opportunity records use a separate V2.1 schema and employer intelligence brief. Existing 19-column person-only Drive exporter and private DPAPI workflow are unchanged. Legacy V1.1 score/20-person goals must not be used to qualify V2.1 opportunities. No real native skill activation or contact authorization has been established by this branch.

# Fadi — Supervised Google Drive Career Review Handoff

**Mission:** Fadi's personal career advancement only. Project ID: PERSONAL_CAREER_OUTREACH.
**Destination:** Existing private Google Drive folder Personal Career Outreach and native Fadi Master Career Outreach Tracker (Prospects and Daily Runs tabs).
**Release status:** Owner-assisted workflow, NOT automatic Codex-to-Google authentication, and NOT confirmed new/contact-ready.

## Security boundaries
- Local encrypted Windows DB is authoritative for identity, suppressions, existing relationships, prior contact and governance. Never export database, DPAPI keys, private notes, messages, recipient emails or approval records to Drive or public Git.
- Codex must never invoke the owner-only private screening commands or defeat the DPAPI sandbox. Owner performs screening in ordinary PowerShell outside Codex.
- Google Sheet statuses are review annotations, not authenticated consent or SEND_AUTHORIZED.
- Google Drive connector access in ChatGPT does not itself give local Codex Google API access.

## First controlled 5-person research run
Use the *native* Codex daily-executive-outreach skill and specialist skills, recording activation evidence. Research five actual people with public sources. Any uninvoked skill remains NOT VERIFIED. Write a JSON file outside Git, e.g. %LOCALAPPDATA%\CareerOutreach\runs\pilot-research.json, with exactly project_id, run_id, date_local and candidates.
Each candidate contains project_id=PERSONAL_CAREER_OUTREACH, person_name, organization, current_title, why_connect, optionally segment (tucson/remote/other), category (hiring-influencer/strategic-connector/hiring-decision-maker/unknown), source URLs (role_source_url,reason_source_url), observed_on, profile_url, route_type (DIRECT/INDIRECT/MANUAL/NO_ROUTE), route_url and provisional score_total. URLs must be visited observed HTTPS sources; no invented address or hiring power. Do not insert keys, private data, drafts, or any contact-ready/sending assertion.

## Export review packet in owner's normal PowerShell
```powershell
cd C:\Nova-Skills\Career-Daily-Outreach
git pull --ff-only
$private = Join-Path $env:LOCALAPPDATA 'CareerOutreach'
$in = Join-Path $private 'runs\pilot-research.json'
$out = Join-Path $private 'runs\pilot-review-001'
.\.venv\Scripts\python.exe .\scripts\prepare_drive_review_packet.py --input $in --out-dir $out
if ($LASTEXITCODE -ne 0) { throw 'Research export failed; stop' }
```

Packet is new, private and non-overwriting. It includes prospects-review.csv (19 columns matching Prospects), daily-run-review.csv (14 columns matching Daily Runs), candidate-batch.json, candidate-public-review.json and manifest.json. Every prospect stays UNCHECKED history, UNVERIFIED novelty, NOT_REVIEWED by Fadi, PENDING_REVIEW or HOLD evidence, with no sending. IDs beginning RESEARCH- are provisional, not proven person identities.

## Protected owner-only batch check (outside Codex)
```powershell
$screen = Join-Path $private 'runs\pilot-screen-001.json'
$review = Join-Path $private 'runs\pilot-reconciliation-001.json'
if ((Test-Path $screen) -or (Test-Path $review)) { throw 'Use unused private file names' }
pwsh -NoProfile -File .\scripts\relationship-batch-check.ps1 -InputFile (Join-Path $out 'candidate-batch.json') | Set-Content -LiteralPath $screen -Encoding utf8
if ($LASTEXITCODE -ne 0) { throw 'Private screening failed' }
.\.venv\Scripts\python.exe .\scripts\reconcile_operator_screening.py --candidates (Join-Path $out 'candidate-public-review.json') --screening $screen --output $review
if ($LASTEXITCODE -ne 0) { throw 'Reconciliation failed' }
```

Never interpret NOT_FOUND_IN_LOCAL_STORE as NEW; it remains NOVELTY_UNVERIFIED_HOLD. A batch fingerprint is a mixup check, not operator authentication. Do not feed full private output back to Codex.

## Publishing to the private Google Sheet
Use the connected Drive tools from an authenticated owner-controlled session, or manual spreadsheet import. BEFORE updates, search the existing Prospects tab for person ID, name and profile to prevent duplicates; update existing rows rather than overwriting. Import only public review rows; do not copy the private screening output or private notes. Preserve all tabs and dashboard formulas. Record a daily report with 0 certified new, 0 confirmed sent. Unapproved drafts stay separate.

Review public evidence and Fadi's career relevance independently. A general organization form is INDIRECT. No sheet edit grants CONTACT_READY, sender authority, or a real outreach outcome. Stop before any communication.

## Release gates
Real native Codex activation evidence for orchestrator/specialists; supervised five-person source/route and owner-screening demonstration; review of Drive output; seven real daily runs; >=40 independently reviewed people; zero unauthorized sends. Until those are independently proven, production remains NO-GO.
