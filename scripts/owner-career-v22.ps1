# OWNER-ONLY V2.2 evidence and preference handoff. Never invoke from Codex.
# Requires existing DPAPI-protected keys, Windows Python venv and intact database.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][ValidateSet("SourceWitness","OwnerReview","VerifyJournal")][string]$Mode,
    [string]$Packet,
    [string]$Out,
    [string[]]$AllowHost,
    [string]$Report,
    [string]$Witness,
    [int]$Index = 0,
    [ValidateSet("PURSUE","RESEARCH_MORE","REJECT")][string]$Decision,
    [string]$Reason
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$stateFile = Join-Path $private "state-key.dpapi"
$identityFile = Join-Path $private "identity-key.dpapi"
$db = Join-Path $private "relationships.sqlite"
foreach ($file in @($python,$stateFile,$identityFile,$db)) {
    if (-not (Test-Path -LiteralPath $file -PathType Leaf)) {
        throw "Owner local Python/DPAPI/relationship store missing. No fallback or migration."
    }
}
if ($Mode -eq "SourceWitness" -and (-not $Packet -or -not $Out -or -not $AllowHost)) {
    throw "SourceWitness requires Packet, Out, and owner-reviewed AllowHost."
}
if ($Mode -eq "OwnerReview" -and (-not $Report -or -not $Witness -or -not $Decision -or -not $Reason)) {
    throw "OwnerReview requires Report, Witness, Decision, and Reason."
}
try {
    $stateEncrypted = (Get-Content -LiteralPath $stateFile -Raw).Trim()
    $identityEncrypted = (Get-Content -LiteralPath $identityFile -Raw).Trim()
    $stateSecure = ConvertTo-SecureString -String $stateEncrypted
    $identitySecure = ConvertTo-SecureString -String $identityEncrypted
    $env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new("", $stateSecure).Password
    $env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new("", $identitySecure).Password
    $env:OUTREACH_DB_PATH = $db
    if ($Mode -eq "SourceWitness") {
        $argv = @("scripts/owner_career_v22_handoff.py","source-witness","--packet",$Packet,"--out",$Out)
        foreach ($hostName in $AllowHost) { $argv += @("--allow-host",$hostName) }
    } elseif ($Mode -eq "OwnerReview") {
        $argv = @("scripts/owner_career_v22_handoff.py","owner-review",
                  "--report",$Report,"--witness",$Witness,"--index",[string]$Index,
                  "--decision",$Decision,"--reason",$Reason)
    } else {
        $argv = @("scripts/owner_career_v22_handoff.py","verify-journal")
    }
    Push-Location $repoRoot
    try {
        & $python @argv
        if ($LASTEXITCODE -ne 0) { throw "Owner V2.2 handoff failed. No permission granted." }
    } finally { Pop-Location }
} finally {
    Remove-Item Env:OUTREACH_STATE_KEY, Env:OUTREACH_IDENTITY_KEY, Env:OUTREACH_DB_PATH -ErrorAction SilentlyContinue
    Remove-Variable stateEncrypted, identityEncrypted, stateSecure, identitySecure -ErrorAction SilentlyContinue
}
