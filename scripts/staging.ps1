#requires -Version 7.0
<#
.SYNOPSIS
  Start the local staging profile, seed it and run the staging smoke check.
.DESCRIPTION
  Uses .env.staging (ports +1000) and project neatsprint-staging, so it can run
  beside the development stack. This is a production-like rehearsal on one
  workstation, not a cloud environment.
#>
[CmdletBinding()]
param(
    [switch]$NoBuild,
    [switch]$Down,
    [int]$TimeoutSeconds = 900
)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not on PATH."
}

if (-not (Test-Path ".env.staging")) {
    Copy-Item ".env.staging.example" ".env.staging"
    Write-Host "Created .env.staging (replace the staging-only secrets before sharing the host)"
}

$envArgs = @("--env-file", ".env.staging", "--profile", "security")

if ($Down) {
    docker compose @envArgs down -v
    exit $LASTEXITCODE
}

try {
    $gateway = (Select-String -Path ".env.staging" -Pattern '^GATEWAY_HTTP_PORT=(.+)$').Matches[0].Groups[1].Value
    $web = (Select-String -Path ".env.staging" -Pattern '^WEB_PORT=(.+)$').Matches[0].Groups[1].Value
    $iam = (Select-String -Path ".env.staging" -Pattern '^IAM_PORT=(.+)$').Matches[0].Groups[1].Value
    $core = (Select-String -Path ".env.staging" -Pattern '^CORE_PORT=(.+)$').Matches[0].Groups[1].Value
    $token = (Select-String -Path ".env.staging" -Pattern '^BOOTSTRAP_TOKEN=(.+)$').Matches[0].Groups[1].Value
} catch {
    throw ".env.staging is missing GATEWAY_HTTP_PORT, WEB_PORT, IAM_PORT, CORE_PORT or BOOTSTRAP_TOKEN."
}

Write-Host "==> Building and starting the staging stack"
if ($NoBuild) {
    docker compose @envArgs up -d
} else {
    docker compose @envArgs up -d --build
}
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$ready = $false
while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-WebRequest "http://localhost:$gateway/ping" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { $ready = $true; break }
    } catch { Start-Sleep -Seconds 3 }
}
if (-not $ready) { throw "Gateway did not become ready. Run: docker compose --env-file .env.staging logs gateway" }

$services = @(
    @{ Name = "iam"; Port = $iam }, @{ Name = "core"; Port = $core },
    @{ Name = "task"; Port = "8103" }, @{ Name = "team"; Port = "8104" },
    @{ Name = "worklog"; Port = "8105" }, @{ Name = "monitoring"; Port = "8106" },
    @{ Name = "chat"; Port = "8107" }, @{ Name = "reports"; Port = "8108" },
    @{ Name = "ai"; Port = "8109" }
)
foreach ($service in $services) {
    $serviceDeadline = (Get-Date).AddSeconds(120)
    $ok = $false
    while ((Get-Date) -lt $serviceDeadline) {
        try {
            $response = Invoke-WebRequest "http://localhost:$($service.Port)/healthz" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { $ok = $true; break }
        } catch { Start-Sleep -Seconds 2 }
    }
    if (-not $ok) { throw "$($service.Name) did not become healthy on :$($service.Port)" }
    Write-Host ("  ok   {0,-12} :{1}" -f $service.Name, $service.Port)
}

Write-Host "==> Seeding demo data"
$env:CORE_INTERNAL_URL = "http://localhost:$core"
$env:IAM_INTERNAL_URL = "http://localhost:$iam"
$env:GATEWAY_URL = "http://localhost:$gateway"
$env:BOOTSTRAP_TOKEN = $token
python "scripts/seed.py"
if ($LASTEXITCODE -ne 0) { throw "seed failed" }

Write-Host "==> Waiting for ClamAV"
$clam = docker compose @envArgs ps --format json clamav | ConvertFrom-Json
$clamDeadline = (Get-Date).AddSeconds(600)
while ((Get-Date) -lt $clamDeadline) {
    $state = docker inspect --format "{{.State.Health.Status}}" $clam.Name 2>$null
    if ($state -eq "healthy") { break }
    Start-Sleep -Seconds 10
}
if ($state -ne "healthy") { Write-Host "ClamAV is not healthy yet; uploads will fail closed." -ForegroundColor Yellow }

Write-Host "==> Smoke check"
$env:BASE_URL = "http://localhost:$gateway/api/v1"
$env:WEB_URL = "http://localhost:$web"
$env:SMOKE_EMAIL = "owner@acme-labs.com"
$env:SMOKE_PASSWORD = "NeatSprint!2026"
python "scripts/smoke/staging_smoke.py"
if ($LASTEXITCODE -ne 0) { throw "staging smoke failed" }

Write-Host ""
Write-Host "Staging is up:"
Write-Host "  Web     http://localhost:$web"
Write-Host "  API     http://localhost:$gateway/api/v1"
Write-Host "  UAT     run docs/UAT.md against this stack"
