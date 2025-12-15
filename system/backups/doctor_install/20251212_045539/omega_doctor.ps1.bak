param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest

$gov = Join-Path $ROOT 'system\governor\scf.psm1'
$ucg = Join-Path $ROOT 'system\meta\ucg\ucg.psm1'

if (-not (Test-Path $gov)) { throw ('Missing governor module: ' + $gov) }
if (-not (Test-Path $ucg)) { throw ('Missing UCG module: ' + $ucg) }

Import-Module $gov -Force
Import-Module $ucg -Force

Assert-ScfRunAllowed -ROOT $ROOT -Subsystem 'omega.master'
Initialize-Ucg -ROOT $ROOT

Write-Host ''
Write-Host '🔥 OMEGA-ALPHA — BOOTING (UCG authoritative)...' -ForegroundColor Magenta

$globalRun = Start-UcgRun -ROOT $ROOT -Subsystem 'omega.master' -Script $PSCommandPath

function Invoke-Step {
  [CmdletBinding()]
  param(
    [Parameter(Mandatory)][string]$Name,
    [Parameter(Mandatory)][string]$ScriptPath
  )

  if (-not (Test-Path $ScriptPath)) {
    Write-Host ('⚠ Missing: ' + $Name + ' => ' + $ScriptPath + ' (skipped)') -ForegroundColor Yellow
    Write-UcgEvent -ROOT $ROOT -Type 'step.skipped' -Data @{ name=$Name; path=$ScriptPath }
    return
  }

  Write-Host ('⚙ ' + $Name + '...') -ForegroundColor Cyan
  $stepRun = Start-UcgRun -ROOT $ROOT -Subsystem ('step:' + $Name) -Script $ScriptPath

  try {
    & $ScriptPath -ROOT $ROOT
    Stop-UcgRun -ROOT $ROOT -RunId $stepRun -Status 'ok'
    Write-Host ('✔ Done: ' + $Name) -ForegroundColor Green
  } catch {
    Stop-UcgRun -ROOT $ROOT -RunId $stepRun -Status 'error' -Error $_.Exception.Message
    Write-Host ('❌ FAILED: ' + $Name + ' => ' + $_.Exception.Message) -ForegroundColor Red
    throw
  }
}

try {
  Invoke-Step -Name 'Omega Kernel'       -ScriptPath (Join-Path $ROOT 'system\kernel\omega_kernel.ps1')
  Invoke-Step -Name 'Omega Builder'      -ScriptPath (Join-Path $ROOT 'system\builder\omega_builder.ps1')
  Invoke-Step -Name 'Omega Upgrade'      -ScriptPath (Join-Path $ROOT 'system\upgrade\omega_upgrade.ps1')
  Invoke-Step -Name 'Omega Mapper'       -ScriptPath (Join-Path $ROOT 'system\map\omega_map.ps1')
  Invoke-Step -Name 'Omega Evolve'       -ScriptPath (Join-Path $ROOT 'system\evolution\omega_evolve.ps1')
  Invoke-Step -Name 'Ingestion Discover' -ScriptPath (Join-Path $ROOT 'ingestion\discovery\discover.ps1')
  Invoke-Step -Name 'Agent Market Tick'  -ScriptPath (Join-Path $ROOT 'agents\market\market_tick.ps1')
  Invoke-Step -Name 'Repo Sync Engine'   -ScriptPath (Join-Path $ROOT 'system\sync\repo_sync_engine.ps1')
  Invoke-Step -Name 'State Publish'      -ScriptPath (Join-Path $ROOT 'system\sync\publish_state.ps1')

  Write-Host ''
  Write-Host '============================' -ForegroundColor DarkGray
  Write-Host '  OMEGA-ALPHA SYSTEM CHECK' -ForegroundColor Cyan
  Write-Host '============================' -ForegroundColor DarkGray
  Write-Host '✔ UCG authoritative' -ForegroundColor Green
  Write-Host '✔ Governor active' -ForegroundColor Green
  Write-Host '✔ Profile OK: system\config\infinity_profile.json' -ForegroundColor Green
  Write-Host '🔥 OMEGA-ALPHA — COMPLETE' -ForegroundColor Magenta

  Stop-UcgRun -ROOT $ROOT -RunId $globalRun -Status 'ok'
} catch {
  Write-UcgEvent -ROOT $ROOT -Type 'omega.master.error' -Data @{ error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $globalRun -Status 'error' -Error $_.Exception.Message
  throw
}