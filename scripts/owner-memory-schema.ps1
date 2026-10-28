# Trusted owner-only memory schema inspection and explicitly approved additive migration.
# NEVER run from Codex's sandbox. NO private data, keys or files enter Git.
[CmdletBinding()]
param(
    [ValidateSet("inspect", "migrate")]
    [string] $Mode = "inspect",
    [string] $Database,
    [switch] $IApproveSchemaChange
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$repoRoot = Split-Path -Parent $PSScriptRoot
$python = Join-Path $repoRoot ".venv\Scripts\python.exe"
$private = Join-Path $env:LOCALAPPDATA "CareerOutreach"
$backupDir = Join-Path $private "backups"
if (-not $Database) { $Database = Join-Path $private "relationships.sqlite" }
$privateFull = [IO.Path]::GetFullPath($private).TrimEnd([IO.Path]::DirectorySeparatorChar)
$databaseFull = [IO.Path]::GetFullPath($Database)
if (-not $databaseFull.StartsWith($privateFull + [IO.Path]::DirectorySeparatorChar,
    [StringComparison]::OrdinalIgnoreCase)) {
    throw "Only private CareerOutreach database paths are permitted."
}
foreach ($path in @($python, $databaseFull)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Required runtime or existing private memory database missing."
    }
}
if ($Mode -eq "inspect") {
    & $python -m outreach_agent.memory_schema_cli inspect --db $databaseFull
    if ($LASTEXITCODE -ne 0) { throw "Read-only schema inspection failed." }
    return
}
if (-not $IApproveSchemaChange) {
    throw "Schema modification requires explicit -IApproveSchemaChange. Inspect first."
}
$stateFile = Join-Path $private "state-key.dpapi"
$identityFile = Join-Path $private "identity-key.dpapi"
foreach ($path in @($stateFile, $identityFile)) {
    if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
        throw "Original DPAPI-protected keys unavailable; migration refused."
    }
}
try {
    $a = (Get-Content -LiteralPath $stateFile -Raw).Trim()
    $b = (Get-Content -LiteralPath $identityFile -Raw).Trim()
    if (-not $a -or -not $b) { throw "Empty key file; migration refused." }
    $stateSecure = ConvertTo-SecureString -String $a
    $identitySecure = ConvertTo-SecureString -String $b
    $env:OUTREACH_STATE_KEY = [System.Net.NetworkCredential]::new("",$stateSecure).Password
    $env:OUTREACH_IDENTITY_KEY = [System.Net.NetworkCredential]::new("",$identitySecure).Password
    & $python -m outreach_agent.memory_schema_cli migrate --db $databaseFull --backups-dir $backupDir --operator-approved
    if ($LASTEXITCODE -ne 0) {
        throw "Migration failed; keep your original database and protected backup."
    }
} finally {
    Remove-Item Env:OUTREACH_STATE_KEY,Env:OUTREACH_IDENTITY_KEY -ErrorAction SilentlyContinue
    Remove-Variable a,b,stateSecure,identitySecure -ErrorAction SilentlyContinue
}
