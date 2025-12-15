param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "map"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "map" -Script $PSCommandPath
try {
  Write-Host "🗺 Omega Mapper — Writing system map..." -ForegroundColor Yellow
  $mapPath = Join-Path $ROOT "system\map\system_map.json"
  $items = Get-ChildItem -Path $ROOT -Recurse -Force -ErrorAction SilentlyContinue |
    Select-Object FullName,Length,LastWriteTime,PsIsContainer
  $items | ConvertTo-Json -Depth 10 | Out-File -FilePath $mapPath -Encoding utf8
  Write-UcgEvent -ROOT $ROOT -Type "map.tick" -Data @{ map_path=$mapPath; count=($items|Measure-Object).Count; status="ok" }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Mapper tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "map.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}