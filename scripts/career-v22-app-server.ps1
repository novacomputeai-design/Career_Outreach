# Operator-run Codex App Server JSONL skill input qualification.
# Does not open private memory or use elevated agents. Never grants contact.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$branch = (& git -C $repo branch --show-current | Out-String).Trim()
if ($LASTEXITCODE -ne 0 -or $branch -ne "feat/career-intelligence-v2-2-e2e-hardening") {
    throw "Expected the V2.2 hardening branch. Stop."
}
$gitStatus = @(& git -C $repo status --porcelain)
if ($LASTEXITCODE -ne 0 -or $gitStatus.Count -ne 0) {
    throw "A clean V2.2 checkout is required. Stop."
}
if ($env:OUTREACH_STATE_KEY -or $env:OUTREACH_IDENTITY_KEY -or $env:OUTREACH_DB_PATH) {
    throw "Protected owner credentials are present. Close this shell and use an ordinary clean session."
}
$python = Join-Path $repo ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "The repository Python virtual environment is missing."
}

$cmd = Get-Command codex.cmd -ErrorAction SilentlyContinue
$codexBin = $null
$codexEntry = $null
if ($null -ne $cmd) {
    $codexBin = $cmd.Source
} else {
    # Some nvm4w installations expose codex.ps1 but lack codex.cmd.
    # Run the package entry directly with Node to avoid shell preference quirks.
    $node = Get-Command node.exe -ErrorAction SilentlyContinue
    if ($null -eq $node) {
        throw "Neither codex.cmd nor node.exe was found."
    }
    $codexBin = $node.Source
    $codexEntry = Join-Path (Split-Path -Parent $node.Source) "node_modules\@openai\codex\bin\codex.js"
    if (-not (Test-Path -LiteralPath $codexEntry -PathType Leaf)) {
        throw "Codex Node entry not available. Do not guess package paths."
    }
}

$adapter = Join-Path $repo "scripts\career_v22_app_server_probe.py"
$argv = @($adapter,"--repo",$repo,"--codex-bin",$codexBin,"--timeout","90")
if ($null -ne $codexEntry) { $argv += @("--codex-entry",$codexEntry) }

& $python @argv
if ($LASTEXITCODE -ne 0) {
    throw "App Server adapter failed; preserve HOLD. No permissions were granted."
}
Write-Output "APP_SERVER_QUALIFICATION=REPORT_ONLY"
Write-Output "LIVE_DPAPI_TEST=NOT_RUN"
Write-Output "OUTBOUND_AUTHORIZED=FALSE"
