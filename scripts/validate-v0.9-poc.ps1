param(
    [string]$SmokeBaseUrl = "http://127.0.0.1:8000",
    [switch]$SkipSmokeApi,
    [switch]$RequireSmokeApi
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
$Warnings = New-Object System.Collections.Generic.List[string]

function Invoke-ValidationStep {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][scriptblock]$ScriptBlock
    )

    Write-Host ""
    Write-Host "== $Name =="
    Set-Location $RepoRoot
    try {
        & $ScriptBlock
    } finally {
        Set-Location $RepoRoot
    }
    if ($LASTEXITCODE -ne 0) {
        throw "Validation step failed: $Name"
    }
    Write-Host "PASS $Name"
}

function Invoke-RgScan {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string[]]$Paths,
        [switch]$WarnOnHit,
        [switch]$RequireHit
    )

    Write-Host ""
    Write-Host "== $Name =="
    $output = & rg -n $Pattern @Paths 2>$null
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        $output | Select-Object -First 120 | ForEach-Object { Write-Host $_ }
        if ($output.Count -gt 120) {
            Write-Host "... scan output truncated after 120 lines"
        }
        if ($WarnOnHit) {
            $Warnings.Add("$Name produced matches that require human review.") | Out-Null
            Write-Warning "$Name produced matches that require human review."
        }
        return
    }

    if ($exitCode -eq 1) {
        if ($RequireHit) {
            throw "$Name did not find expected v0.9 sandbox boundary terms."
        }
        Write-Host "No matches."
        return
    }

    throw "$Name failed to run rg."
}

Push-Location $RepoRoot
try {
    Write-Host "Validating v0.9 Douyin Provider POC readiness package"
    Write-Host "Repository: $RepoRoot"

    Invoke-ValidationStep "git diff --check" {
        git diff --check
    }

    Invoke-ValidationStep "backend tests" {
        if (Test-Path ".\scripts\test-backend.ps1") {
            & .\scripts\test-backend.ps1
        } else {
            Push-Location ".\backend"
            try {
                .\.venv\Scripts\python.exe -m pytest
            } finally {
                Pop-Location
            }
        }
    }

    Invoke-ValidationStep "frontend tests" {
        Push-Location ".\frontend"
        try {
            npm.cmd run test -- --run
        } finally {
            Pop-Location
        }
    }

    Invoke-ValidationStep "frontend build" {
        if (Test-Path ".\scripts\build-frontend.ps1") {
            & .\scripts\build-frontend.ps1
        } else {
            Push-Location ".\frontend"
            try {
                npm.cmd run build
            } finally {
                Pop-Location
            }
        }
    }

    if ($SkipSmokeApi) {
        $Warnings.Add("smoke-api was skipped by request.") | Out-Null
        Write-Warning "smoke-api was skipped by request."
    } else {
        try {
            Invoke-ValidationStep "smoke-api" {
                & .\scripts\smoke-api.ps1 -BaseUrl $SmokeBaseUrl
            }
        } catch {
            if ($RequireSmokeApi) {
                throw
            }
            $Warnings.Add("smoke-api did not pass against $SmokeBaseUrl. Start a local backend or rerun with -RequireSmokeApi for strict mode.") | Out-Null
            Write-Warning "smoke-api did not pass against $SmokeBaseUrl. Start a local backend or rerun with -RequireSmokeApi for strict mode."
        }
    }

    Invoke-RgScan `
        -Name "misleading current-capability wording scan" `
        -Pattern "production ready now|commercial ready now|SaaS ready now|v1\.5 completed|v2\.0 completed|real Douyin integration completed|real OAuth implemented|real publish implemented|real metrics implemented|published to Douyin|real publish success" `
        -Paths @("README.md", "README.en.md", "docs", "frontend", "backend") `
        -WarnOnHit

    Invoke-RgScan `
        -Name "completion wording scan" `
        -Pattern "v0\.9 POC completed|v1\.0 completed|v1\.5 completed|v2\.0 completed|production[-]ready|commercial[-]ready|SaaS[-]ready" `
        -Paths @("README.md", "README.en.md", "docs", "frontend", "backend") `
        -WarnOnHit

    Invoke-RgScan `
        -Name "sensitive field-name scan" `
        -Pattern "access_token|refresh_token|client_secret|authorization_code|oauth_state|api_key|credential|cookie|session|bearer|password|secret" `
        -Paths @("README.md", "README.en.md", "docs", "frontend", "backend", "scripts") `
        -WarnOnHit

    Invoke-RgScan `
        -Name "sandbox boundary keyword scan" `
        -Pattern "sandbox|dry-run|simulated|douyin_sandbox|douyin_real|blocked|not implemented|POC|release candidate" `
        -Paths @("README.md", "README.en.md", "docs", "frontend", "backend", "scripts") `
        -RequireHit

    Write-Host ""
    Write-Host "== git status --short =="
    $status = git status --short
    if ($status) {
        $status | ForEach-Object { Write-Host $_ }
        $Warnings.Add("git status --short is not empty; this is expected before committing intended Batch 8 changes but must be clean after commit.") | Out-Null
        Write-Warning "git status --short is not empty; ensure only intended Batch 8 files are staged and committed."
    } else {
        Write-Host "Clean working tree."
    }

    Write-Host ""
    Write-Host "== verification summary =="
    if ($Warnings.Count -gt 0) {
        Write-Host "Completed with warnings that require human review:"
        $Warnings | ForEach-Object { Write-Host "- $_" }
    } else {
        Write-Host "Completed with no warnings."
    }
} finally {
    Pop-Location
}
