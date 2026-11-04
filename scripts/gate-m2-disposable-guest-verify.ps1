# OWNER-ONLY inside the SAME disposable guest as gate-m2-disposable-guest-seed.ps1
# Unlocks only guest DPAPI keys to verify a recovered SYNTHETIC database READ ONLY.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$RestoredDb
)
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
if ([Environment]::OSVersion.Platform -ne [PlatformID]::Win32NT) { throw "M2_WINDOWS_ONLY" }
$model = Get-CimInstance Win32_ComputerSystem -ErrorAction Stop
if ("$($model.Manufacturer) $($model.Model)" -notmatch "(?i)(virtual|vmware|hyper-v|virtualbox|qemu|kvm|xen|parallels)") {
    throw "M2_DISPOSABLE_GUEST_NOT_RECOGNIZED"
}
$marker = Join-Path $env:SystemDrive "CAREER_M2_DISPOSABLE_GUEST.marker"
if (-not (Test-Path -LiteralPath $marker -PathType Leaf)) { throw "M2_DISPOSABLE_GUEST_MARKER_MISSING" }
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
if (-not (Test-Path -LiteralPath $python -PathType Leaf)) { throw "M2_GUEST_VENV_MISSING" }
$stateFile = Join-Path $private "state-key.dpapi"
$identityFile = Join-Path $private "identity-key.dpapi"
if (-not (Test-Path -LiteralPath $stateFile -PathType Leaf) -or
    -not (Test-Path -LiteralPath $identityFile -PathType Leaf)) {
    throw "M2_GUEST_TEST_ONLY_KEYS_MISSING"
}
$backups = [IO.Path]::GetFullPath((Join-Path $private "backups")).TrimEnd([IO.Path]::DirectorySeparatorChar)
$check = [IO.Path]::GetFullPath($RestoredDb)
if (-not $check.StartsWith($backups + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
    throw "M2_RECOVERY_MUST_REMAIN_UNDER_GUEST_BACKUP_PATH"
}
try {
    $state = ConvertTo-SecureString -String (Get-Content $stateFile -Raw).Trim()
    $identity = ConvertTo-SecureString -String (Get-Content $identityFile -Raw).Trim()
    $env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new("", $state).Password
    $env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new("", $identity).Password
    $env:CAREER_M2_DISPOSABLE_VM_CONFIRMED = "YES"
    Push-Location $repoRoot
    try {
        & $python -m scripts.gate_m2_disposable_guest_fixture --private-root $private --verify-restored $check
        if ($LASTEXITCODE -ne 0) { throw "M2_RESTORED_SYNTHETIC_DB_NOT_VERIFIED" }
    } finally {
        Pop-Location
    }
} finally {
    Remove-Item Env:OUTREACH_STATE_KEY, Env:OUTREACH_IDENTITY_KEY, Env:CAREER_M2_DISPOSABLE_VM_CONFIRMED -ErrorAction SilentlyContinue
    Remove-Variable state, identity -ErrorAction SilentlyContinue
}
