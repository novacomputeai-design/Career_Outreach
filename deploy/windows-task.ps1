# Installer example. Verify secrets are available to the task account before use.
param([string]$RepoPath = (Get-Location).Path,
      [string]$PythonPath = "$RepoPath\.venv\Scripts\python.exe",
      [string]$RunAt = "07:00")
$ErrorActionPreference = "Stop"
if (!(Test-Path $PythonPath)) { throw "Create the venv and install requirements first" }
if (!$env:OUTREACH_DB_PATH -or !$env:TAVILY_API_KEY -or !$env:OPENAI_API_KEY -or !$env:OUTREACH_STATE_KEY -or !$env:OUTREACH_IDENTITY_KEY) {
  throw "Private DB path and research/state credentials are required"
}
if ($env:OUTREACH_DB_PATH.StartsWith($RepoPath,[StringComparison]::OrdinalIgnoreCase)) {
  throw "Database cannot be in this public repository"
}
$runDir = Join-Path $env:LOCALAPPDATA "CareerOutreach"
New-Item -Path $runDir -ItemType Directory -Force | Out-Null
$outFile = Join-Path $runDir "latest-report.json"
$cmd = ('"{0}" -m outreach_agent run --out "{1}"' -f $PythonPath,$outFile)
$action = New-ScheduledTaskAction -Execute "cmd.exe" -Argument ("/c " + $cmd) -WorkingDirectory $RepoPath
$trigger = New-ScheduledTaskTrigger -Daily -At $RunAt
$settings = New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Hours 3)
Register-ScheduledTask -TaskName "Personal Executive Outreach Research" -Action $action -Trigger $trigger -Settings $settings -Force
Write-Output "Scheduled research only. Verify task account, secrets, report and execution logs."
