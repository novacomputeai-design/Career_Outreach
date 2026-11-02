# Owner-launched, read-only Codex CLI native skill discovery probe.
# Records raw host JSONL in TEMP; this does NOT certify native activation.
# No private history, DPAPI access, live research, or repository modifications.
[CmdletBinding()]
param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$repo = Split-Path -Parent $PSScriptRoot
$expected = "feat/career-intelligence-v2-2-e2e-hardening"
$branch = (& git -C $repo branch --show-current).Trim()
if ($LASTEXITCODE -ne 0 -or $branch -ne $expected) {
    throw "Wrong branch: $branch. Expected $expected."
}
if ((& git -C $repo status --porcelain).Count -gt 0) {
    throw "Working tree not clean. Do not run a qualification with mixed sources."
}
if ($env:OUTREACH_STATE_KEY -or $env:OUTREACH_IDENTITY_KEY -or $env:OUTREACH_DB_PATH) {
    throw "Private relationship credentials detected in environment. Clear them."
}
if (-not (Get-Command codex -ErrorAction SilentlyContinue)) {
    throw "Codex executable not found on PATH."
}
$folder = Join-Path $env:TEMP ("career-native-skill-probe-" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Force -Path $folder | Out-Null
$stdout = Join-Path $folder "codex-host-events.jsonl"
$stderr = Join-Path $folder "codex-stderr.txt"
$version = (& codex --version | Out-String).Trim()

$prompt = @'
Use the native $daily-executive-outreach skill explicitly. If the host supports it, also invoke $provenance-and-freshness and $run-quality-audit through supported native skill mechanisms.

Task: Diagnose native skill discovery and invocation ONLY. Do not conduct any employer research, browse the web, edit files, execute scripts, access private memory, inspect Windows user folders, use DPAPI, send outreach, or apply for jobs.

Report the exact names of the repository-local skills that the host makes available, the activation mechanism you actually used, and which evidence comes from HOST events rather than merely reading SKILL.md. If this Codex host does not expose such evidence, say NOT_VERIFIED. Do not fabricate a skill invocation event.
'@

Push-Location $repo
try {
    # Explicit read-only sandbox, no --full-auto or workspace-write.
    & codex exec --json --sandbox read-only $prompt 1> $stdout 2> $stderr
    $exitCode = $LASTEXITCODE
} finally {
    Pop-Location
}
$types = @()
if (Test-Path -LiteralPath $stdout) {
    foreach ($line in Get-Content -LiteralPath $stdout) {
        try {
            $event = $line | ConvertFrom-Json -ErrorAction Stop
            if ($null -ne $event.type) { $types += [string]$event.type }
        } catch {
            # Preserve raw evidence for owner review. Do not infer success.
        }
    }
}
Write-Output "CODEX_VERSION=$version"
Write-Output "EXIT_CODE=$exitCode"
Write-Output "RAW_HOST_EVENTS=$stdout"
Write-Output "STDERR_LOG=$stderr"
Write-Output "EVENT_TYPES=$(([string[]]($types | Sort-Object -Unique)) -join ',')"
Write-Output "NATIVE_SKILL_INVOCATION=NOT_INDEPENDENTLY_VERIFIED_BY_THIS_SCRIPT"
Write-Output "DPAPI_ACCESSED=FALSE_BY_PROCEDURE_NOT_HOST_ATTESTED"
Write-Output "OUTBOUND_AUTHORIZED=FALSE"

# Review and redact the JSONL before sharing it; host events may contain
# environment paths, user-generated prompt content, or other sensitive text.
# A zero exit code or a model saying "used skill" is not native proof.
if ($exitCode -ne 0) { throw "Codex diagnostic exited $exitCode. Inspect local stderr." }
