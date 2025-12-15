param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "evolution"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "evolution" -Script $PSCommandPath
try {
  Write-Host "🌱 Omega Evolution — Tick..." -ForegroundColor Yellow
  $log = Join-Path $ROOT "system\evolution\evolution_log.txt"
  "Tick: $(Get-Date -Format o)" | Out-File $log -Append -Encoding utf8
  Write-UcgEvent -ROOT $ROOT -Type "evolution.tick" -Data @{ log_path=$log; status="ok" }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Evolution tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "evolution.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}