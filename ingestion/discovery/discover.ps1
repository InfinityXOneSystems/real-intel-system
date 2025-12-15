param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

Import-Module (Join-Path $ROOT "system\governor\scf.psm1") -Force
Import-Module (Join-Path $ROOT "system\meta\ucg\ucg.psm1") -Force

Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "ingestion.discovery"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "ingestion.discovery" -Script $PSCommandPath

try {
  Write-Host "Ingestion Discovery - Tick (hotfix)" -ForegroundColor Cyan

  $safe = ($env:INFINITY_SAFE_MODE -eq "1")
  $out  = Join-Path $ROOT "ingestion\discovery\discovery_state.json"
  $dir  = Split-Path -Parent $out
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

  @{
    ts=(Get-Date).ToString("o")
    safe_mode=$safe
    discovered_sources=@()
    note=$(if($safe){"safe_mode: network ingest disabled"}else{"discovery scaffold: wire crawlers next"})
  } | ConvertTo-Json -Depth 10 | Out-File -FilePath $out -Encoding utf8

  Write-UcgEvent -ROOT $ROOT -Type "ingestion.discovery.tick" -Data @{ out_path=$out; status="ok"; safe_mode=$safe }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "Discovery OK" -ForegroundColor Green
} catch {
  $err = $_.Exception.Message
  try { Write-UcgEvent -ROOT $ROOT -Type "ingestion.discovery.tick" -Data @{ status="error"; error=$err } } catch {}
  try { Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $err } catch {}
  throw
}