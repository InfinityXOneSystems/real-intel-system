param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

Import-Module (Join-Path $ROOT "system\governor\scf.psm1") -Force
Import-Module (Join-Path $ROOT "system\meta\ucg\ucg.psm1") -Force

Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "omega.map"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "omega.map" -Script $PSCommandPath

try {
  Write-Host "Omega Mapper - Running (hotfix)" -ForegroundColor Cyan

  $out = Join-Path $ROOT "system\map\system_map.json"
  $dir = Split-Path -Parent $out
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

  @{
    ts=(Get-Date).ToString("o")
    root=$ROOT
    note="map scaffold (hotfix): wire inventory next"
  } | ConvertTo-Json -Depth 10 | Out-File -FilePath $out -Encoding utf8

  Write-UcgEvent -ROOT $ROOT -Type "omega.map.tick" -Data @{ status="ok"; out_path=$out }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "Mapper OK" -ForegroundColor Green
} catch {
  $err = $_.Exception.Message
  try { Write-UcgEvent -ROOT $ROOT -Type "omega.map.tick" -Data @{ status="error"; error=$err } } catch {}
  try { Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $err } catch {}
  throw
}