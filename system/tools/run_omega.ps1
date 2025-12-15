$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest
. "$PSScriptRoot\enter_root.ps1"
if (-not (Test-Path $MASTER)) { throw "omega_master.ps1 not found: $MASTER" }
Write-Host "🚀 Running Omega Master..." -ForegroundColor Cyan
& $MASTER -ROOT $ROOT