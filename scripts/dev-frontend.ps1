$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$FrontendDir = Join-Path $RepoRoot "frontend"
$NodeModules = Join-Path $FrontendDir "node_modules"

Set-Location $FrontendDir

if (-not (Test-Path $NodeModules)) {
    Write-Host "Installing frontend dependencies..."
    npm.cmd install
}

Write-Host "Starting frontend at http://localhost:5173"
npm.cmd run dev
