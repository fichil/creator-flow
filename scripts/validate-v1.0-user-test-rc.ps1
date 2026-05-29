param(
    [switch]$SkipTests
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

function Invoke-RgReviewScan {
    param(
        [Parameter(Mandatory = $true)][string]$Name,
        [Parameter(Mandatory = $true)][string]$Pattern,
        [Parameter(Mandatory = $true)][string[]]$Paths,
        [switch]$WarnOnHit,
        [switch]$FailOnHit
    )

    Write-Host ""
    Write-Host "== $Name =="
    $output = & rg -n --pcre2 $Pattern @Paths 2>$null
    $exitCode = $LASTEXITCODE

    if ($exitCode -eq 0) {
        $output | Select-Object -First 120 | ForEach-Object { Write-Host $_ }
        if ($output.Count -gt 120) {
            Write-Host "... scan output truncated after 120 lines"
        }
        if ($FailOnHit) {
            throw "$Name found forbidden matches."
        }
        if ($WarnOnHit) {
            $Warnings.Add("$Name produced matches that require human review.") | Out-Null
            Write-Warning "$Name produced matches that require human review."
        }
        return
    }

    if ($exitCode -eq 1) {
        Write-Host "No matches."
        return
    }

    throw "$Name failed to run rg."
}

function Get-TrackedReviewPaths {
    $paths = @(git ls-files) + @(git ls-files --others --exclude-standard)
    return $paths | Where-Object {
        $_ -and
        (Test-Path $_) -and
        ($_ -notmatch '(^|/)(node_modules|dist|\.venv|uploads|runtime)(/|$)') -and
        ($_ -notmatch '\.(sqlite|sqlite3|db)$')
    }
}

function Test-LocalOnlySchemaForbiddenColumns {
    $modelsPath = Join-Path $RepoRoot "backend/app/db/models.py"
    $content = Get-Content -Raw -Encoding utf8 $modelsPath
    $tables = @(
        "provider_oauth_states",
        "provider_credential_references",
        "publish_intents",
        "publish_attempts",
        "publish_status_reconciliations",
        "publish_status_snapshots",
        "publish_metrics_snapshots"
    )
    $forbidden = @(
        "raw_authorization_code",
        "authorization_code",
        "raw_state",
        "state_value",
        "oauth_state",
        "access_token",
        "refresh_token",
        "client_secret",
        "api_key",
        "cookie",
        "session",
        "bearer",
        "raw_request",
        "raw_response",
        "provider_response",
        "upload_response",
        "publish_response",
        "status_response",
        "metrics_response",
        "external_response",
        "douyin_response"
    )

    foreach ($table in $tables) {
        $pattern = "CREATE TABLE IF NOT EXISTS $table \((?s).*?\n\);"
        $match = [regex]::Match($content, $pattern)
        if (-not $match.Success) {
            throw "Schema table not found: $table"
        }
        foreach ($term in $forbidden) {
            if ($match.Value -match "(?m)^\s*$term\s") {
                throw "Forbidden column '$term' found in $table"
            }
        }
    }
}

function Test-RcClosureReadiness {
    $requiredFiles = @(
        "docs/releases/v1.0-rc-closure-audit.md",
        "docs/releases/v1.0-tag-readiness-checklist.md",
        "docs/releases/v1.0-merge-readiness-checklist.md"
    )

    foreach ($path in $requiredFiles) {
        $fullPath = Join-Path $RepoRoot $path
        if (-not (Test-Path $fullPath)) {
            throw "Required RC closure artifact missing: $path"
        }
    }

    $rcChecklistPath = Join-Path $RepoRoot "docs/releases/v1.0-user-test-rc-checklist.md"
    $rcChecklist = Get-Content -Raw -Encoding utf8 $rcChecklistPath
    if ($rcChecklist -notmatch "7b70ae6bf647c15018a29fbc040dcd4ceeac50e9") {
        throw "RC checklist does not contain the Batch 10 commit SHA."
    }

    $finalTag = git tag --list "v1.0.0"
    if ($finalTag) {
        throw "Forbidden final tag exists: v1.0.0"
    }

    $rcTags = git tag --list "v1.0.0-rc*"
    if ($rcTags) {
        throw "Forbidden RC tag exists for this closure task."
    }
}

function Test-RcMarkdownFormatting {
    $rcMarkdownFiles = [ordered]@{
        "docs/releases/v1.0-rc-closure-audit.md" = 35
        "docs/releases/v1.0-tag-readiness-checklist.md" = 30
        "docs/releases/v1.0-merge-readiness-checklist.md" = 30
        "docs/releases/v1.0-user-test-rc-checklist.md" = 80
        "docs/releases/v1.0-user-test-release-notes-draft.md" = 40
        "docs/releases/v1.0-pr-description-draft.md" = 50
        "docs/testing/v1.0-user-test-guide.md" = 50
        "docs/testing/v1.0-user-test-rc-test-matrix.md" = 50
        "docs/operations/v1.0-user-test-rollback-disablement.md" = 50
        "docs/decisions/0055-v1.0-user-test-readiness-release-candidate.md" = 40
    }
    $issues = New-Object System.Collections.Generic.List[string]

    foreach ($entry in $rcMarkdownFiles.GetEnumerator()) {
        $path = $entry.Key
        $minimumLineCount = $entry.Value
        $fullPath = Join-Path $RepoRoot $path
        if (-not (Test-Path $fullPath)) {
            $issues.Add("${path}: target RC Markdown file is missing.") | Out-Null
            continue
        }

        $bytes = [System.IO.File]::ReadAllBytes($fullPath)
        if ($bytes.Length -eq 0) {
            $issues.Add("${path}: document is empty.") | Out-Null
            continue
        }

        $lfCount = 0
        $crCount = 0
        foreach ($byte in $bytes) {
            if ($byte -eq 10) {
                $lfCount += 1
            }
            if ($byte -eq 13) {
                $crCount += 1
            }
        }

        $realLfLineCount = $lfCount + 1
        if ($realLfLineCount -lt $minimumLineCount) {
            $issues.Add("${path}: document has only ${realLfLineCount} real LF lines; minimum is ${minimumLineCount}.") | Out-Null
        }
        if (($crCount -gt 0) -and ($lfCount -eq 0)) {
            $issues.Add("${path}: document appears to use CR-only newlines.") | Out-Null
        }

        $text = [System.Text.Encoding]::UTF8.GetString($bytes)
        $lines = @($text -split "`n")
        $firstLine = $lines[0].TrimEnd("`r")
        if ($firstLine -notmatch '^#\s+\S.+$') {
            $issues.Add("${path}: first line must be a standalone H1 heading.") | Out-Null
        }
        if (
            ($firstLine -match '##\s+') -or
            ($firstLine -match '- \[ \]') -or
            ($firstLine -match '^\#\s+.+\s-\s+') -or
            ($firstLine -match '^# .+\S\s+(This document|This checklist|This guide|This runbook|These notes|It does|It is|Status:)')
        ) {
            $issues.Add("${path}: first line appears to include paragraph text beyond a standalone title.") | Out-Null
        }

        $inFence = $false
        for ($index = 0; $index -lt $lines.Count; $index += 1) {
            $line = $lines[$index].TrimEnd("`r")
            $lineNumber = $index + 1
            if ($line.TrimStart().StartsWith('```')) {
                $inFence = -not $inFence
                continue
            }
            if ($inFence) {
                continue
            }

            if ($line -match '^#\s+.+##\s+') {
                $issues.Add("${path}:${lineNumber}: H1 heading appears to share a line with a later heading.") | Out-Null
            }
            if (($line -match '##\s+') -and ($line -match '-')) {
                $issues.Add("${path}:${lineNumber}: H2 heading appears to share a line with a list marker.") | Out-Null
            }
            if ([regex]::Matches($line, '- \[ \]').Count -ge 2) {
                $issues.Add("${path}:${lineNumber}: multiple checklist items may share one line.") | Out-Null
            }
            if (($line -match '^\s*[-*]\s+') -and ($line -match '\s[-*]\s+')) {
                $issues.Add("${path}:${lineNumber}: multiple bullet items may share one line.") | Out-Null
            }
            if (($line -match '^\s{0,3}#{1,6}\s+') -and ($index + 1 -lt $lines.Count) -and ($lines[$index + 1].Trim() -ne '')) {
                $issues.Add("${path}:${lineNumber}: heading is not followed by a blank line.") | Out-Null
            }
            $isLinkOrTableLine = (
                ($line -match 'https?://') -or
                ($line -match '\[[^\]]+\]\([^)]+\)') -or
                ($line -match '^\s*\|')
            )
            if (($line.Length -gt 300) -and (-not $isLinkOrTableLine) -and ($line -notmatch '^\s*$')) {
                $issues.Add("${path}:${lineNumber}: ordinary line is longer than 300 characters.") | Out-Null
            }
        }
    }

    if ($issues.Count -eq 0) {
        Write-Host "No RC Markdown formatting issues found."
        return
    }

    $issues | Select-Object -First 80 | ForEach-Object { Write-Host $_ }
    if ($issues.Count -gt 80) {
        Write-Host "... scan output truncated after 80 lines"
    }
    throw "RC Markdown formatting scan found blocking issues."
}

Push-Location $RepoRoot
try {
    Write-Host "Validating v1.0 user test release candidate package"
    Write-Host "Repository: $RepoRoot"

    Invoke-ValidationStep "git diff --check" {
        git diff --check
    }

    if ($SkipTests) {
        $Warnings.Add("Automated tests were skipped by request.") | Out-Null
        Write-Warning "Automated tests were skipped by request."
    } else {
        Invoke-ValidationStep "backend tests" {
            Push-Location ".\backend"
            try {
                .\.venv\Scripts\python.exe -m pytest -q
            } finally {
                Pop-Location
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
            Push-Location ".\frontend"
            try {
                npm.cmd run build
            } finally {
                Pop-Location
            }
        }
    }

    Invoke-ValidationStep "local-only schema forbidden column scan" {
        Test-LocalOnlySchemaForbiddenColumns
    }

    Invoke-ValidationStep "RC closure readiness checks" {
        Test-RcClosureReadiness
    }

    Invoke-ValidationStep "RC Markdown formatting checks" {
        Test-RcMarkdownFormatting
    }

    $reviewPaths = @(Get-TrackedReviewPaths)

    Invoke-RgReviewScan `
        -Name "high-confidence sensitive value scan" `
        -Pattern "(sk-[A-Za-z0-9]{20,}|AKIA[0-9A-Z]{16}|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|xox[baprs]-[A-Za-z0-9-]{10,}|-----BEGIN (RSA |EC |OPENSSH |)PRIVATE KEY-----|Bearer\s+[A-Za-z0-9._~+/=-]{20,}|api[_-]?key\s*[:=]\s*['""][A-Za-z0-9._-]{16,}|access[_-]?token\s*[:=]\s*['""][A-Za-z0-9._-]{16,}|refresh[_-]?token\s*[:=]\s*['""][A-Za-z0-9._-]{16,}|client[_-]?secret\s*[:=]\s*['""][A-Za-z0-9._-]{16,})" `
        -Paths $reviewPaths `
        -FailOnHit

    $forbiddenCapabilityPattern = @(
        "v1\.0\s+final\s+released",
        "v1\.0\.0\s+released",
        "v1\.0\s+is\s+complete",
        "v1\.0\s+completed",
        "real\s+Douyin\s+OAuth\s+implemented",
        "real\s+Douyin\s+publish\s+is\s+available",
        "real\s+Douyin\s+metrics\s+fetched",
        "real\s+status\s+query\s+enabled",
        "OAuth\s+is\s+implemented"
    ) -join "|"

    Invoke-RgReviewScan `
        -Name "forbidden affirmative capability wording scan" `
        -Pattern "($forbiddenCapabilityPattern)" `
        -Paths @("README.md", "README.en.md", "docs", "frontend", "backend") `
        -FailOnHit

    Invoke-RgReviewScan `
        -Name "readiness wording review scan" `
        -Pattern "(production[-]ready|commercial[-]ready|SaaS[-]ready)" `
        -Paths @("README.md", "README.en.md", "docs", "frontend", "backend") `
        -WarnOnHit

    Invoke-RgReviewScan `
        -Name "business external call route review scan" `
        -Pattern "(oauth/start|oauth/callback|authorization-url|oauth-url|token-exchange|credential-storage|scheduled-publish|metrics-query|status-query|douyin_real/.*/publish|douyin_real/.*/metrics)" `
        -Paths @("backend/app/api/routes", "frontend/src", "docs") `
        -WarnOnHit

    Invoke-RgReviewScan `
        -Name "required RC artifact scan" `
        -Pattern "(0055-v1\.0-user-test-readiness-release-candidate|v1\.0-user-test-rc-checklist|v1\.0-rc-closure-audit|v1\.0-tag-readiness-checklist|v1\.0-merge-readiness-checklist|v1\.0-user-test-release-notes-draft|v1\.0-pr-description-draft|v1\.0-user-test-guide|v1\.0-user-test-rollback-disablement|v1\.0-user-test-rc-test-matrix)" `
        -Paths @("README.md", "README.en.md", "docs", "scripts") `
        -WarnOnHit

    Write-Host ""
    Write-Host "== git status --short =="
    $status = git status --short
    if ($status) {
        $status | ForEach-Object { Write-Host $_ }
        $Warnings.Add("git status --short is not empty; this is expected before committing intended Batch 10 files but must be clean after commit.") | Out-Null
        Write-Warning "git status --short is not empty; ensure only intended Batch 10 files are staged and committed."
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
