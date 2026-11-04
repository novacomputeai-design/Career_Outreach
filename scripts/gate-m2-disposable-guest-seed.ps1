# OWNER-ONLY Gate M2 bootstrap inside a NEW, disposable Windows guest.
# Never run on the host profile or from Codex. No real CareerOutreach content.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][switch]$ConfirmDisposableGuest
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $ConfirmDisposableGuest) { throw "M2_DISPOSABLE_GUEST_CONFIRMATION_REQUIRED" }
if (-not $IsWindows -and $PSVersionTable.PSEdition -eq "Core") {
    throw "M2_WINDOWS_ONLY"
}
$model = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
$guestModel = "$($model.Manufacturer) $($model.Model)"
if ($guestModel -notmatch "(?i)(virtual|vmware|hyper-v|virtualbox|qemu|kvm|xen|parallels)") {
    throw "M2_VM_ATTESTATION_UNAVAILABLE: Guest model not recognized. Stop; never weaken this guard on the host."
}
$marker = Join-Path $env:SystemDrive "CAREER_M2_DISPOSABLE_GUEST.marker"
if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) {
    throw "M2_GUEST_MARKER_MISSING: Create this marker manually INSIDE a disposable VM only."
}
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
if (Test-Path -LiteralPath $private) {
    throw "M2_EXISTING_PRIVATE_FOLDER: Stop; never write to existing owner data."
}
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) {
    throw "M2_GUEST_PYTHON_VENV_MISSING"
}
$phrase = "I CONFIRM THIS IS A DISPOSABLE WINDOWS GUEST"
$entered = Read-Host "Type exactly '$phrase' to create a TEST-ONLY CareerOutreach folder"
if ($entered -cne $phrase) { throw "M2_OWNER_CONFIRMATION_MISMATCH" }

# Secrets are generated in memory, DPAPI-protected under the disposable guest
# Windows user, never echoed, written plaintext, passed on command line or committed.
$keys = @(& $python -c 'from cryptography.fernet import Fernet; import secrets; print(Fernet.generate_key().decode()); print(secrets.token_hex(32))')
if ($LASTEXITCODE -ne 0 -or $keys.Count -ne 2) {
    throw "M2_GUEST_KEY_GENERATION_FAILED"
}
$env:OUTREACH_STATE_KEY = [string]$keys[0]
$env:OUTREACH_IDENTITY_KEY = [string]$keys[1]
$env:CAREER_M2_DISPOSABLE_VM_CONFIRMED = "YES"

try {
    # The guard above verified this path did not exist; force creation to fail
    # if something creates it concurrently rather than writing existing data.
    [IO.Directory]::CreateDirectory($private) | Out-Null
    foreach ($spec in @(
        @{ Value = $env:OUTREACH_STATE_KEY; File = "state-key.dpapi" },
        @{ Value = $env:OUTREACH_IDENTITY_KEY; File = "identity-key.dpapi" }
    )) {
        $protected = ConvertFrom-SecureString (
            ConvertTo-SecureString -String $spec.Value -AsPlainText -Force
        )
        $dest = Join-Path $private $spec.File
        if (Test-Path -LiteralPath $dest) { throw "M2_SECRET_DESTINATION_EXISTS" }
        [IO.File]::WriteAllText($dest, $protected)
    }
    Push-Location $repoRoot
    try {
        & $python -m scripts.gate_m2_disposable_guest_fixture --private-root $private
        if ($LASTEXITCODE -ne 0) {
            throw "M2_SYNTHETIC_FIXTURE_FAILED: Discard the disposable VM."
        }
    } finally {
        Pop-Location
    }
    Write-Host "M2_DISPOSABLE_GUEST_SEEDED — synthetic only; no source truth or approval authority."
} finally {
    Remove-Item Env:OUTREACH_STATE_KEY, Env:OUTREACH_IDENTITY_KEY, Env:CAREER_M2_DISPOSABLE_VM_CONFIRMED -ErrorAction SilentlyContinue
    Remove-Variable keys -ErrorAction SilentlyContinue
}
