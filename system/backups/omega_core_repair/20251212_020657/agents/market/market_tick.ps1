param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "agent.market"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "agent.market" -Script $PSCommandPath
try {
  Write-Host "🐝 Agent Market — Tick..." -ForegroundColor Cyan
  $out = Join-Path $ROOT "agents\market\market_state.json"
  @{
    ts=(Get-Date).ToString("o")
    agents=@()
    tasks=@()
    note="market scaffold: wire auctions + reputation next"
  } | ConvertTo-Json -Depth 10 | Out-File -FilePath $out -Encoding utf8
  Write-UcgEvent -ROOT $ROOT -Type "agent.market.tick" -Data @{ out_path=$out; status="ok" }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Market tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "agent.market.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}