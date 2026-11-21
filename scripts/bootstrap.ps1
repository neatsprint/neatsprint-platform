#requires -Version 7.0
<#
.SYNOPSIS
  Bootstrap the NeatSprint local stack.
.DESCRIPTION
  Checks Docker, creates .env from .env.example, builds and starts the stack,
  then waits for the gateway and every service health endpoint.
#>
[CmdletBinding()]
param(
    [switch]$NoBuild,
    [switch]$NoSeed,
    [int]$TimeoutSeconds = 600
)

$ErrorActionPreference = "Stop"
Set-Location (Join-Path $PSScriptRoot "..")

function Write-Step($message) {
    Write-Host "==> $message" -ForegroundColor Cyan
}

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    throw "Docker is not installed or not on PATH."
}

docker info *> $null
if ($LASTEXITCODE -ne 0) {
    throw "Docker is not running. Start Docker Desktop and retry."
}

if (-not (Test-Path ".env")) {
    Copy-Item ".env.example" ".env"
    Write-Step "Created .env from .env.example (local development defaults)"
}

Write-Step "Starting the stack"
if ($NoBuild) {
    docker compose up -d
} else {
    docker compose up -d --build
}
if ($LASTEXITCODE -ne 0) { throw "docker compose up failed" }

$deadline = (Get-Date).AddSeconds($TimeoutSeconds)
$gatewayReady = $false
while ((Get-Date) -lt $deadline) {
    try {
        $response = Invoke-WebRequest "http://localhost:8000/ping" -UseBasicParsing -TimeoutSec 2
        if ($response.StatusCode -eq 200) { $gatewayReady = $true; break }
    } catch { Start-Sleep -Seconds 3 }
}
if (-not $gatewayReady) { throw "Gateway did not become ready within $TimeoutSeconds seconds. Run: docker compose logs gateway" }

$services = @(
    @{ Name = "iam"; Port = 8001 },
    @{ Name = "core"; Port = 8002 },
    @{ Name = "task"; Port = 8003 },
    @{ Name = "team"; Port = 8004 },
    @{ Name = "worklog"; Port = 8005 },
    @{ Name = "monitoring"; Port = 8006 },
    @{ Name = "chat"; Port = 8007 },
    @{ Name = "reports"; Port = 8008 },
    @{ Name = "ai"; Port = 8009 }
)

$failed = @()
foreach ($service in $services) {
    $ready = $false
    $serviceDeadline = (Get-Date).AddSeconds(90)
    while ((Get-Date) -lt $serviceDeadline) {
        try {
            $response = Invoke-WebRequest "http://localhost:$($service.Port)/healthz" -UseBasicParsing -TimeoutSec 2
            if ($response.StatusCode -eq 200) { $ready = $true; break }
        } catch { Start-Sleep -Seconds 2 }
    }
    if ($ready) {
        Write-Host ("  ok   {0,-12} :{1}" -f $service.Name, $service.Port) -ForegroundColor Green
    } else {
        Write-Host ("  fail {0,-12} :{1}" -f $service.Name, $service.Port) -ForegroundColor Red
        $failed += $service.Name
    }
}

Write-Step "NeatSprint is up"
Write-Host "  Web            http://localhost:3000"
Write-Host "  API gateway    http://localhost:8000/api/v1"
Write-Host "  Traefik        http://localhost:8089"
Write-Host "  MinIO console  http://localhost:9001"
Write-Host "  Mailpit        http://localhost:8025"
Write-Host "  Grafana        http://localhost:3001   (docker compose --profile observability up -d)"

if ($failed.Count -gt 0) {
    Write-Host "Unhealthy: $($failed -join ', '). Inspect with: docker compose logs <service>" -ForegroundColor Yellow
    exit 1
}

if (-not $NoSeed) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        Write-Step "Seeding the demo tenant"
        python "scripts/seed.py"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Seed failed. Inspect: docker compose logs neatsprint-core neatsprint-iam" -ForegroundColor Yellow
            exit 1
        }
    } else {
        Write-Host "python not found; skip seeding (run scripts/seed.py manually)" -ForegroundColor Yellow
    }
}
