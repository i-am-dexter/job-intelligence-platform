# Job Intelligence Platform - run locally (Windows PowerShell)
# Starts the backend (SQLite) and frontend as separate background jobs.
# Run .\setup.ps1 first if you haven't already.

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$backendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location "$root\backend"
    $env:DATABASE_URL = "sqlite:///./job_intelligence.db"
    & ".\.venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000
} -ArgumentList $root

$frontendJob = Start-Job -ScriptBlock {
    param($root)
    Set-Location "$root\frontend"
    npm run dev
} -ArgumentList $root

Write-Host "Backend starting on http://localhost:8000 (job id $($backendJob.Id))"
Write-Host "Frontend starting on http://localhost:3000 (job id $($frontendJob.Id))"
Write-Host "Press Ctrl+C to stop, then run: Stop-Job $($backendJob.Id),$($frontendJob.Id)"

try {
    Receive-Job -Job $backendJob, $frontendJob -Wait
} finally {
    Stop-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob, $frontendJob -ErrorAction SilentlyContinue
}
