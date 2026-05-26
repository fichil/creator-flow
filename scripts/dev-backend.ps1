$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$BackendDir = Join-Path $RepoRoot "backend"
$VenvPython = Join-Path $BackendDir ".venv\Scripts\python.exe"

Set-Location $BackendDir

if (-not (Test-Path $VenvPython)) {
    Write-Host "Creating backend virtual environment..."
    py -3.11 -m venv .venv
}

Write-Host "Installing backend dependencies..."
& $VenvPython -m pip install -e ".[test]"

Write-Host "Starting backend at http://127.0.0.1:8000"
& $VenvPython -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
