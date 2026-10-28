# Operator-only Windows DPAPI read-only batch check.
# MUST be executed in normal owner PowerShell, never from Codex's sandbox.
# Private JSON input stays in %LOCALAPPDATA%\CareerOutreach; no DB writes.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$false)]
    [string]$InputFile
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
if (-not $InputFile) { $InputFile = Join-Path $private "candidate-batch.json" }
$privateFull = [System.IO.Path]::GetFullPath($private).TrimEnd([IO.Path]::DirectorySeparatorChar)
$inputFull = [System.IO.Path]::GetFullPath($InputFile)
if (-not $inputFull.StartsWith($privateFull + [IO.Path]::DirectorySeparatorChar,
                             [StringComparison]::OrdinalIgnoreCase)) {
    throw "Batch input must reside under the user's private CareerOutreach directory."
}

$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$stateFile = Join-Path $private "state-key.dpapi"
$identityFile = Join-Path $private "identity-key.dpapi"
$db = Join-Path $private "relationships.sqlite"
foreach ($path in @($python, $stateFile, $identityFile, $db, $inputFull)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required local runtime, protected memory, or batch input missing. Fail closed."
    }
}

try {
    $stateEncrypted = (Get-Content -LiteralPath $stateFile -Raw).Trim()
    $identityEncrypted = (Get-Content -LiteralPath $identityFile -Raw).Trim()
    if (-not $stateEncrypted -or -not $identityEncrypted) {
        throw "Protected key file empty. Fail closed."
    }
    $stateSecure = ConvertTo-SecureString -String $stateEncrypted
    $identitySecure = ConvertTo-SecureString -String $identityEncrypted
    $env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new("", $stateSecure).Password
    $env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new("", $identitySecure).Password
    $env:OUTREACH_DB_PATH = $db

    & $python -m outreach_agent relationship-batch-check --input $inputFull
    if ($LASTEXITCODE -ne 0) {
        throw "Protected read-only batch screening failed; no novelty can be assumed."
    }
}
finally {
    Remove-Item Env:OUTREACH_STATE_KEY, Env:OUTREACH_IDENTITY_KEY, Env:OUTREACH_DB_PATH -ErrorAction SilentlyContinue
    Remove-Variable stateEncrypted, identityEncrypted, stateSecure, identitySecure -ErrorAction SilentlyContinue
}
