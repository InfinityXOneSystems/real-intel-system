param([string]$ROOT)
$ErrorActionPreference="Stop"; Set-StrictMode -Version Latest
Import-Module "$ROOT\system\governor\scf.psm1" -Force
Import-Module "$ROOT\system\meta\ucg\ucg.psm1" -Force
Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "upgrade"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "upgrade" -Script $PSCommandPath
try {
  Write-Host "🔧 Omega Upgrade — Self-heal pass (non-destructive)..." -ForegroundColor Yellow
  $mode = Get-ScfMode -ROOT $ROOT
  $budget = [int]$mode.budgets.max_files_changed_per_tick
  $changed = 0

  # UTF-8 no BOM sanitizer for .ps1/.json under system only (safe scope)
  $targets = Get-ChildItem -Path (Join-Path $ROOT "system") -Recurse -Force -ErrorAction SilentlyContinue |
    Where-Object { -not $_.PSIsContainer -and ($_.Extension -in @(".ps1",".json")) }

  foreach($f in $targets){
    if($changed -ge $budget){ break }
    try {
      $bytes = [System.IO.File]::ReadAllBytes($f.FullName)
      # BOM: EF BB BF
      if($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF){
        $text = [System.Text.UTF8Encoding]::new($true).GetString($bytes)
        $utf8NoBom = New-Object System.Text.UTF8Encoding($false)
        [System.IO.File]::WriteAllText($f.FullName, $text, $utf8NoBom)
        $changed++
      }
    } catch {}
  }

  # Compact UCG if it grows large
  Compact-UcgEvents -ROOT $ROOT -MaxLines 20000

  Write-UcgEvent -ROOT $ROOT -Type "upgrade.tick" -Data @{
    status="ok"
    files_sanitized=$changed
    destructive_allowed=$false
    note="system-scope self-heal + UCG compaction"
  }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
  Write-Host "✔ Upgrade tick complete." -ForegroundColor Green
} catch {
  Write-UcgEvent -ROOT $ROOT -Type "upgrade.tick" -Data @{ status="error"; error=$_.Exception.Message }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $_.Exception.Message
  throw
}