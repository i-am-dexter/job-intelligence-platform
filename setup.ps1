# Job Intelligence Platform - one-time setup (Windows PowerShell)
# Prepares .env, backend virtualenv, and frontend dependencies for local (non-Docker) use.

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path

if (-not (Test-Path "$root\.env")) {
    Copy-Item "$root\.env.example" "$root\.env"
    Write-Host "Created .env from .env.example -- edit it to add ANTHROPIC_API_KEY if desired."
}

Write-Host "Setting up backend..."
Push-Location "$root\backend"
python -m venv .venv
& ".\.venv\Scripts\pip.exe" install -r requirements.txt

$env:DATABASE_URL = "sqlite:///./job_intelligence.db"
& ".\.venv\Scripts\alembic.exe" upgrade head
Pop-Location

Write-Host "Setting up frontend..."
Push-Location "$root\frontend"
if (-not (Test-Path ".env.local")) {
    "NEXT_PUBLIC_API_BASE_URL=http://localhost:8000" | Out-File -Encoding utf8 ".env.local"
}
npm install
Pop-Location

Write-Host "Setup complete. Run .\run.ps1 to start the app."
