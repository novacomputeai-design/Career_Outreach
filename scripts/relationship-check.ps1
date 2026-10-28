# Windows DPAPI-backed, read-only identity check for the Codex agent.
# Scope: one explicit person-name/profile lookup; returns only classification.
# Run in a separate PowerShell process to avoid exposing key env vars to Codex:
# pwsh -NoProfile -File .\scripts\relationship-check.ps1 -PersonName "Example Person"
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateNotNullOrEmpty()]
    [string] $PersonName,

    [Parameter(Mandatory = $false)]
    [string] $ProfileUrl
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$stateFile = Join-Path $private "state-key.dpapi"
$identityFile = Join-Path $private "identity-key.dpapi"
$db = Join-Path $private "relationships.sqlite"

foreach ($path in @($python, $stateFile, $identityFile, $db)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required local runtime, encrypted credentials, or database unavailable. Fail closed."
    }
}

try {
    # DPAPI files can be decrypted only under the corresponding Windows account.
    # Do not log these values, put them in command-line arguments, or write them to disk.
    $stateEncrypted = (Get-Content -LiteralPath $stateFile -Raw).Trim()
    $identityEncrypted = (Get-Content -LiteralPath $identityFile -Raw).Trim()
    if (-not $stateEncrypted -or -not $identityEncrypted) {
        throw "Encrypted credential file is empty. Fail closed."
    }

    $stateSecure = ConvertTo-SecureString -String $stateEncrypted
    $identitySecure = ConvertTo-SecureString -String $identityEncrypted

    $env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new("", $stateSecure).Password
    $env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new("", $identitySecure).Password
    $env:OUTREACH_DB_PATH = $db

    $arguments = @("-m", "outreach_agent", "relationship-check", "--person-name", $PersonName)
    if ($ProfileUrl) { $arguments += @("--profile-url", $ProfileUrl) }

    # Standard output is only the minimal relationship classification from cli.py.
    & $python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Read-only relationship check failed. Do not infer novelty."
    }
}
finally {
    Remove-Item Env:OUTREACH_STATE_KEY, Env:OUTREACH_IDENTITY_KEY, Env:OUTREACH_DB_PATH -ErrorAction SilentlyContinue
    Remove-Variable stateEncrypted, identityEncrypted, stateSecure, identitySecure -ErrorAction SilentlyContinue
}
