# Desktop agent prerequisite check (Windows).
# Usage: ./scripts/check-desktop-prereqs.ps1 [-Quiet]
# Exit code 0 when every required prerequisite is present, 1 otherwise.

param([switch]$Quiet)

$rows = @()

function Add-Row {
    param(
        [string]$Name,
        [ValidateSet("OK", "MISSING", "WARN")]
        [string]$Status,
        [string]$Detail,
        [string]$Fix,
        [switch]$Required
    )
    $script:rows += [pscustomobject]@{
        Name     = $Name
        Status   = $Status
        Detail   = $Detail
        Fix      = $Fix
        Required = [bool]$Required
    }
}

function Get-CommandPath([string]$Name) {
    $cmd = Get-Command $Name -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}

# Rust
$rustc = Get-CommandPath "rustc"
$cargo = Get-CommandPath "cargo"
$rustup = Get-CommandPath "rustup"
if ($rustc -and $cargo) {
    $version = (& rustc --version) -replace "^rustc ", ""
    $hostLine = (& rustc -vV | Select-String "^host:")
    $hostTriple = ($hostLine -split ":", 2)[1].Trim()
    if ($hostTriple -like "*msvc*") {
        Add-Row "rust (rustc + cargo)" "OK" "$version, host $hostTriple" "" -Required
    } else {
        Add-Row "rust (rustc + cargo)" "WARN" "$version, host $hostTriple" "rustup default stable-x86_64-pc-windows-msvc" -Required
    }
} else {
    Add-Row "rust (rustc + cargo)" "MISSING" "" "winget install --id Rustlang.Rustup -e" -Required
}

if ($rustup) {
    Add-Row "rustup" "OK" (& rustup --version | Select-Object -First 1) "" -Required
} else {
    Add-Row "rustup" "MISSING" "" "winget install --id Rustlang.Rustup -e" -Required
}

if ($rustup) {
    $components = (& rustup component list --installed 2>$null) -join " "
    $missing = @()
    if ($components -notmatch "rustfmt") { $missing += "rustfmt" }
    if ($components -notmatch "clippy") { $missing += "clippy" }
    if ($missing.Count -eq 0) {
        Add-Row "rustfmt + clippy" "OK" "" ""
    } else {
        Add-Row "rustfmt + clippy" "MISSING" ($missing -join ", ") "rustup component add rustfmt clippy"
    }
}

# MSVC C++ build tools
$vswhere = "C:\Program Files (x86)\Microsoft Visual Studio\Installer\vswhere.exe"
if (Test-Path $vswhere) {
    $vsPath = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationPath 2>$null
    $vsVersion = & $vswhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -property installationVersion 2>$null
    if ($vsPath) {
        Add-Row "MSVC v143 (C++ tools)" "OK" (Split-Path $vsPath -Leaf) "" -Required
    } else {
        Add-Row "MSVC v143 (C++ tools)" "MISSING" "no VC.Tools component" "winget install --id Microsoft.VisualStudio.2022.BuildTools -e --override `"--wait --passive --add Microsoft.VisualStudio.Workload.VCTools --includeRecommended`"" -Required
    }
} else {
    Add-Row "MSVC v143 (C++ tools)" "MISSING" "vswhere not found" "winget install --id Microsoft.VisualStudio.2022.BuildTools -e" -Required
}

# Windows SDK
$sdkRoot = "C:\Program Files (x86)\Windows Kits\10\Include"
if (Test-Path $sdkRoot) {
    $sdk = Get-ChildItem $sdkRoot -Directory | Where-Object { $_.Name -match "^10\.0\.\d+" } |
        Sort-Object Name -Descending | Select-Object -First 1
    if ($sdk) {
        Add-Row "Windows SDK" "OK" $sdk.Name "" -Required
    } else {
        Add-Row "Windows SDK" "MISSING" "no 10.0.x version" "Add the Windows 11 SDK component to Build Tools" -Required
    }
} else {
    Add-Row "Windows SDK" "MISSING" "$sdkRoot not found" "Add the Windows 11 SDK component to Build Tools" -Required
}

# WebView2
$webviewKeys = @(
    "HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}",
    "HKCU:\SOFTWARE\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}"
)
$webview = $null
foreach ($key in $webviewKeys) {
    $pv = (Get-ItemProperty $key -ErrorAction SilentlyContinue).pv
    if ($pv) { $webview = $pv; break }
}
if ($webview) {
    Add-Row "WebView2 runtime" "OK" $webview "" -Required
} else {
    Add-Row "WebView2 runtime" "MISSING" "" "winget install --id Microsoft.EdgeWebView2Runtime -e" -Required
}

# Node + npm
$node = Get-CommandPath "node"
if ($node) {
    $nodeVersion = (& node --version).TrimStart("v")
    $major = [int]($nodeVersion.Split(".")[0])
    if ($major -ge 22) {
        Add-Row "node" "OK" "v$nodeVersion" ""
    } else {
        Add-Row "node" "WARN" "v$nodeVersion" "nvm install 22; nvm use 22"
    }
} else {
    Add-Row "node" "MISSING" "" "nvm install 22 (or winget install OpenJS.NodeJS.LTS)" -Required
}

$npm = Get-CommandPath "npm"
if ($npm) {
    Add-Row "npm" "OK" (& npm --version) ""
} else {
    Add-Row "npm" "MISSING" "" "comes with Node.js" -Required
}

# Git
$git = Get-CommandPath "git"
if ($git) {
    Add-Row "git" "OK" (& git --version) ""
} else {
    Add-Row "git" "MISSING" "" "winget install --id Git.Git -e"
}

# SQLCipher native build helpers
$nasm = Get-CommandPath "nasm"
if ($nasm) {
    Add-Row "nasm (OpenSSL build)" "OK" (& nasm -v) ""
} else {
    Add-Row "nasm (OpenSSL build)" "WARN" "only needed for bundled-sqlcipher-vendored-openssl" "winget install --id NASM.NASM -e"
}

$perl = Get-CommandPath "perl"
if ($perl) {
    Add-Row "perl (OpenSSL build)" "OK" ((& perl -v | Select-String "This is perl") -replace "^\s+", "") ""
} else {
    Add-Row "perl (OpenSSL build)" "WARN" "only needed for bundled-sqlcipher-vendored-openssl" "winget install --id StrawberryPerl.StrawberryPerl -e"
}

$winget = Get-CommandPath "winget"
Add-Row "winget" $(if ($winget) { "OK" } else { "WARN" }) $(if ($winget) { & winget --version } else { "install commands above will not work" }) ""

$requiredMissing = @($rows | Where-Object { $_.Required -and $_.Status -ne "OK" })
$warnings = @($rows | Where-Object { $_.Status -eq "WARN" })

if (-not $Quiet) {
    Write-Host ""
    Write-Host "NeatSprint desktop agent prerequisites" -ForegroundColor Cyan
    Write-Host ("-" * 78)
    foreach ($row in $rows) {
        $color = switch ($row.Status) { "OK" { "Green" } "WARN" { "Yellow" } default { "Red" } }
        $detail = if ($row.Detail) { "  $($row.Detail)" } else { "" }
        Write-Host ("{0,-9} {1,-28}{2}" -f $row.Status, $row.Name, $detail) -ForegroundColor $color
        if ($row.Fix) { Write-Host ("          fix: {0}" -f $row.Fix) -ForegroundColor DarkGray }
    }
    Write-Host ("-" * 78)
}

if ($requiredMissing.Count -gt 0) {
    if (-not $Quiet) {
        Write-Host ("{0} required prerequisite(s) missing." -f $requiredMissing.Count) -ForegroundColor Red
        Write-Host "See docs/DESKTOP_AGENT_SETUP.md for the install steps." -ForegroundColor DarkGray
    }
    exit 1
}

if ($warnings.Count -gt 0) {
    if (-not $Quiet) { Write-Host ("Desktop prerequisites look ready ({0} warning(s))." -f $warnings.Count) -ForegroundColor Yellow }
} elseif (-not $Quiet) {
    Write-Host "Desktop prerequisites look ready." -ForegroundColor Green
}
exit 0
