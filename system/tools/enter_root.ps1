$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
$ROOT = "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems"
if (-not (Test-Path (Join-Path $ROOT "system"))) { throw "Root missing system folder: $ROOT" }
Set-Location $ROOT
$SYSTEM = Join-Path $ROOT "system"
$MASTER = Join-Path $SYSTEM "omega_master.ps1"
Write-Host "✅ INFINITY ROOT: $ROOT" -ForegroundColor Green
Write-Host "   MASTER: $MASTER" -ForegroundColor DarkGray