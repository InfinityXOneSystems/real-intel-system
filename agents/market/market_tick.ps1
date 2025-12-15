param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

Import-Module (Join-Path $ROOT "system\governor\scf.psm1") -Force
Import-Module (Join-Path $ROOT "system\meta\ucg\ucg.psm1") -Force

Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "agent.market"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "agent.market" -Script $PSCommandPath

try {
  Write-Host "Agent Market - Tick (hotfix)" -ForegroundColor Cyan

  $out = Join-Path $ROOT "agents\market\market_state.json"
  $dir = Split-Path -Parent $out
  if (-not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

  @{
    ts=(Get-Date).ToString("o")
    agents=@()
    tasks=@()
    note="market scaffold (hotfix): wire auctions + reputation next"
  } | ConvertTo-Json -Depth 10 | Out-File -FilePath $out -Encoding utf8

  Write-UcgEvent -ROOT $ROOT -Type "agent.market.tick" -Data @{ out_path=$out; status="ok" }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "Market OK" -ForegroundColor Green
} catch {
  $err = $_.Exception.Message
  try { Write-UcgEvent -ROOT $ROOT -Type "agent.market.tick" -Data @{ status="error"; error=$err } } catch {}
  try { Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $err } catch {}
  throw
}