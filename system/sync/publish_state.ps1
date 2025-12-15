param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

Import-Module (Join-Path $ROOT "system\governor\scf.psm1") -Force
Import-Module (Join-Path $ROOT "system\meta\ucg\ucg.psm1") -Force

Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "state.publish"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "state.publish" -Script $PSCommandPath

try {
  Write-Host "State Publish - Running (hotfix)" -ForegroundColor Cyan

  $out = Join-Path $ROOT "system\sync\published_state.json"
  $dir = Split-Path -Parent $out
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

  $payload = [ordered]@{
    ts   = (Get-Date).ToString("o")
    root = $ROOT
    note = "publish scaffold (hotfix)"
    paths = @{
      system_map      = (Join-Path $ROOT "system\map\system_map.json")
      discovery_state = (Join-Path $ROOT "ingestion\discovery\discovery_state.json")
    }
  }

  $payload | ConvertTo-Json -Depth 20 | Out-File -FilePath $out -Encoding utf8

  Write-UcgEvent -ROOT $ROOT -Type "state.publish.tick" -Data @{ status="ok"; out_path=$out }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "Publish OK" -ForegroundColor Green
} catch {
  $err = $_.Exception.Message
  try { Write-UcgEvent -ROOT $ROOT -Type "state.publish.tick" -Data @{ status="error"; error=$err } } catch {}
  try { Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $err } catch {}
  throw
}