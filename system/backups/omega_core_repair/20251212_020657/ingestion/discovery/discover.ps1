param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "ingestion.discovery"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "ingestion.discovery" -Script $PSCommandPath
try {
  Write-Host "🕸️ Ingestion Discovery — Tick..." -ForegroundColor Cyan
  $safe = ($env:INFINITY_SAFE_MODE -eq "1")
  $out = Join-Path $ROOT "ingestion\discovery\discovery_state.json"
  @{
    ts=(Get-Date).ToString("o")
    safe_mode=$safe
    discovered_sources=@()
    note=$(if($safe){"safe_mode: network ingest disabled"}else{"discovery scaffold: wire crawlers next"})
  } | ConvertTo-Json -Depth 10 | Out-File -FilePath $out -Encoding utf8
  Write-UcgEvent -ROOT $ROOT -Type "ingestion.discovery.tick" -Data @{ out_path=$out; status="ok"; safe_mode=$safe }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Discovery tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "ingestion.discovery.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}