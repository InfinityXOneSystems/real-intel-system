param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "kernel"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "kernel" -Script $PSCommandPath
try {
  Write-Host "🔥 Omega Kernel — Running (UCG authoritative)..." -ForegroundColor Magenta
  $out = Join-Path $ROOT "system\kernel\omega_reasoning.json"
  @{
    timestamp=(Get-Date).ToString("o")
    status="kernel operational"
    safe_mode=($env:INFINITY_SAFE_MODE -eq "1")
    note="UCG/SCF wired; authoritative memory substrate online"
  } | ConvertTo-Json -Depth 10 | Out-File -FilePath $out -Encoding utf8
  Write-UcgEvent -ROOT $ROOT -Type "kernel.tick" -Data @{ out_path=$out; status="ok" }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Kernel tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "kernel.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}