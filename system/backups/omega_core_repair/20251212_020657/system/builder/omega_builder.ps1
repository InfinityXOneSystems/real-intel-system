param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "builder"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "builder" -Script $PSCommandPath
try {
  Write-Host "🛠 Omega Builder — Ensuring canonical directories..." -ForegroundColor Yellow
  $modules = @(
    "system\kernel","system\builder","system\upgrade","system\map","system\evolution",
    "system\meta\ucg","system\governor","system\credentials","system\sync",
    "Repositories","ingestion\discovery","agents\market"
  )
  $created=@()
  foreach($m in $modules){
    $p = Join-Path $ROOT $m
    if(-not (Test-Path $p)){ New-Item -ItemType Directory -Force -Path $p | Out-Null; $created += $m }
  }
  Write-UcgEvent -ROOT $ROOT -Type "builder.tick" -Data @{ created=$created; status="ok" }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Builder tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "builder.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}