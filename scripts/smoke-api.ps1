param(
    [string]$BaseUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

function Invoke-CreatorFlowJson {
    param(
        [Parameter(Mandatory = $true)][string]$Method,
        [Parameter(Mandatory = $true)][string]$Path,
        [object]$Body = $null
    )

    $uri = "$BaseUrl$Path"
    if ($null -eq $Body) {
        return Invoke-RestMethod -Method $Method -Uri $uri
    }

    return Invoke-RestMethod `
        -Method $Method `
        -Uri $uri `
        -ContentType "application/json" `
        -Body ($Body | ConvertTo-Json -Depth 10)
}

function Assert-Condition {
    param(
        [Parameter(Mandatory = $true)][bool]$Condition,
        [Parameter(Mandatory = $true)][string]$Message
    )

    if (-not $Condition) {
        throw "Smoke check failed: $Message"
    }
}

try {
    Write-Host "Running API smoke checks against $BaseUrl"

    $health = Invoke-CreatorFlowJson -Method "GET" -Path "/api/health"
    Assert-Condition ($health.status -eq "ok") "health endpoint did not return ok"
    Write-Host "PASS health"

    $suffix = Get-Date -Format "yyyyMMddHHmmss"
    $project = Invoke-CreatorFlowJson `
        -Method "POST" `
        -Path "/api/projects" `
        -Body @{ title = "Smoke project $suffix"; description = "Created by local smoke-api.ps1" }
    Assert-Condition ($project.status -eq "draft") "new project is not draft"
    Write-Host "PASS create project #$($project.id)"

    $updated = Invoke-CreatorFlowJson `
        -Method "PATCH" `
        -Path "/api/projects/$($project.id)" `
        -Body @{ title = "Smoke project updated $suffix"; description = "Updated by local smoke-api.ps1" }
    Assert-Condition ($updated.title -like "Smoke project updated*") "project title was not updated"
    Write-Host "PASS update project"

    $textMaterial = Invoke-CreatorFlowJson `
        -Method "POST" `
        -Path "/api/projects/$($project.id)/materials/text" `
        -Body @{ material_type = "text"; title = "Smoke text"; text_content = "Explicit smoke text material." }
    Assert-Condition ($textMaterial.material_type -eq "text") "text material type mismatch"
    Write-Host "PASS add text material"

    $linkMaterial = Invoke-CreatorFlowJson `
        -Method "POST" `
        -Path "/api/projects/$($project.id)/materials/link" `
        -Body @{ title = "Smoke link"; source_url = "https://example.com/smoke" }
    Assert-Condition ($linkMaterial.material_type -eq "link") "link material type mismatch"
    Write-Host "PASS add link material"

    $detail = Invoke-CreatorFlowJson -Method "GET" -Path "/api/projects/$($project.id)"
    Assert-Condition ($detail.status -eq "materials_ready") "project did not become materials_ready"
    Assert-Condition ($detail.materials.Count -ge 2) "project detail did not include expected materials"
    Write-Host "PASS project detail"

    $archived = Invoke-CreatorFlowJson -Method "POST" -Path "/api/projects/$($project.id)/archive"
    Assert-Condition ($archived.status -eq "archived") "project did not archive"
    Write-Host "PASS archive project"

    $defaultProjects = Invoke-CreatorFlowJson -Method "GET" -Path "/api/projects"
    $defaultMatch = @($defaultProjects | Where-Object { $_.id -eq $project.id })
    Assert-Condition ($defaultMatch.Count -eq 0) "archived project appeared in default project list"
    Write-Host "PASS default list hides archived"

    $allProjects = Invoke-CreatorFlowJson -Method "GET" -Path "/api/projects?include_archived=true"
    $archivedMatch = @($allProjects | Where-Object { $_.id -eq $project.id -and $_.status -eq "archived" })
    Assert-Condition ($archivedMatch.Count -eq 1) "include_archived=true did not return archived project"
    Write-Host "PASS include_archived list"

    Write-Host "All API smoke checks passed."
} catch {
    Write-Error $_
    exit 1
}
