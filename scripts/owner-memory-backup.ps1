# Owner-only Windows backup/verification/recovery proof.
# MUST run in trusted user's ordinary PowerShell, NEVER inside Codex sandbox.
# Original state + identity keys stay in user DPAPI, no plaintext keys on command line.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("backup","verify","restore-new")]
    [string] $Mode,

    [string] $Snapshot,

    [string] $Destination
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$backupDir = Join-Path $private "backups"
$stateFile = Join-Path $private "state-key.dpapi"
$identityFile = Join-Path $private "identity-key.dpapi"
$database = Join-Path $private "relationships.sqlite"

if (-not (Test-Path -LiteralPath $backupDir -PathType Container)) {
    New-Item -Path $backupDir -ItemType Directory | Out-Null
}
$privateRoot = [IO.Path]::GetFullPath($private).TrimEnd([IO.Path]::DirectorySeparatorChar)

function Assert-PrivatePath {
    param([string] $PathToCheck)
    $p = [IO.Path]::GetFullPath($PathToCheck)
    if (-not $p.StartsWith($privateRoot + [IO.Path]::DirectorySeparatorChar,
                           [StringComparison]::OrdinalIgnoreCase)) {
        throw "Backup/recovery paths must remain under the private CareerOutreach folder."
    }
    return $p
}

foreach ($p in @($python, $stateFile, $identityFile)) {
    if (-not (Test-Path -LiteralPath $p -PathType Leaf)) {
        throw "Required Python runtime or DPAPI-protected key file missing. Fail closed."
    }
}

if ($Mode -eq "backup") {
    if (-not (Test-Path -LiteralPath $database -PathType Leaf)) {
        throw "Source private SQLite file unavailable. No backup attempted."
    }
    $filename = "relationships-" + [DateTime]::UtcNow.ToString("yyyyMMdd-HHmmss-fffffff") + "-" +
        [Guid]::NewGuid().ToString("N").Substring(0,8) + ".fernet"
    $Snapshot = Join-Path $backupDir $filename
} elseif (-not $Snapshot) {
    throw "Verify and restore-new require -Snapshot (existing encrypted .fernet backup)."
}
$Snapshot = Assert-PrivatePath $Snapshot

if ($Mode -eq "restore-new") {
    if (-not $Destination) {
        $filename = "recovery-proof-" + [Guid]::NewGuid().ToString("N") + ".sqlite"
        $Destination = Join-Path $backupDir $filename
    }
    $Destination = Assert-PrivatePath $Destination
}
if ($Mode -ne "backup" -and -not (Test-Path -LiteralPath $Snapshot -PathType Leaf)) {
    throw "Encrypted snapshot missing; cannot verify or restore."
}
try {
    $stateEncrypted = (Get-Content -LiteralPath $stateFile -Raw).Trim()
    $identityEncrypted = (Get-Content -LiteralPath $identityFile -Raw).Trim()
    if (-not $stateEncrypted -or -not $identityEncrypted) {
        throw "Encrypted key file empty. Fail closed."
    }
    $stateSecure = ConvertTo-SecureString -String $stateEncrypted
    $identitySecure = ConvertTo-SecureString -String $identityEncrypted
    $env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new("",$stateSecure).Password
    $env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new("",$identitySecure).Password

    $arguments = @("-m","outreach_agent.memory_recovery_cli",$Mode)
    if ($Mode -eq "backup") {
        $arguments += @("--db",$database,"--out",$Snapshot)
    } elseif ($Mode -eq "verify") {
        $arguments += @("--snapshot",$Snapshot)
    } else {
        $arguments += @("--snapshot",$Snapshot,"--destination",$Destination)
    }
    & $python @arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Protected memory $Mode failed. Never infer recovery readiness."
    }
    if ($Mode -eq "backup") { Write-Host "Encrypted snapshot: $Snapshot" }
    if ($Mode -eq "restore-new") { Write-Host "Recovery copy (NOT live DB): $Destination" }
} finally {
    Remove-Item Env:OUTREACH_STATE_KEY,Env:OUTREACH_IDENTITY_KEY -ErrorAction SilentlyContinue
    Remove-Variable stateEncrypted,identityEncrypted,stateSecure,identitySecure -ErrorAction SilentlyContinue
}
