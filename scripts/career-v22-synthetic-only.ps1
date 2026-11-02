# Synthetic-only local engineering rehearsal; does not unlock DPAPI or contact services.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
$branch = (& git -C $root branch --show-current)
if ($LASTEXITCODE -ne 0 -or $branch -ne "feat/career-intelligence-v2-2-e2e-hardening") {
    throw "Wrong repository branch. Use the draft V2.2 hardening branch."
}
if ($env:OUTREACH_STATE_KEY -or $env:OUTREACH_IDENTITY_KEY -or $env:OUTREACH_DB_PATH) {
    throw "Protected owner credentials found in this environment. Clear them first."
}
$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "Python virtual environment missing; no fallback to an unknown interpreter."
}
Push-Location $root
try {
    & $python -m unittest discover -s tests -p "test_career_*.py" -v
    if ($LASTEXITCODE -ne 0) {
        throw "Synthetic trust-boundary rehearsal FAILED. Do not qualify live E2E."
    }
    Write-Output "SYNTHETIC_BOUNDARY_REHEARSAL=PASS"
    Write-Output "LIVE_DPAPI_TEST=NOT_RUN"
    Write-Output "NATIVE_CODEX_HOST_TEST=NOT_RUN"
    Write-Output "PUBLIC_WEB_TEXT_TEST=NOT_RUN"
    Write-Output "CONTACT_AUTHORIZED=FALSE"
} finally {
    Pop-Location
}
