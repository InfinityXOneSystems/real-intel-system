param(
  [Parameter(Mandatory)][string]$ROOT,
  [ValidateSet("scan","repair","loop")][string]$Mode = "repair",
  [switch]$Apply,
  [int]$IntervalSec = 180,
  [int]$JitterSec   = 30
)

$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

function Write-Utf8NoBom([string]$Path, [string]$Content) {
  $dir = Split-Path -Parent $Path
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  $enc = New-Object System.Text.UTF8Encoding($false)
  [System.IO.File]::WriteAllText($Path, $Content, $enc)
}

function Acquire-FileLock([string]$LockPath) {
  $dir = Split-Path -Parent $LockPath
  if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  try {
    return [System.IO.File]::Open($LockPath,[System.IO.FileMode]::OpenOrCreate,[System.IO.FileAccess]::ReadWrite,[System.IO.FileShare]::None)
  } catch [System.IO.IOException] { return $null }
}

function Parse-Ok([string]$Path) {
  try { [scriptblock]::Create((Get-Content -Raw -Path $Path)) | Out-Null; return $true } catch { return $false }
}

function Log([string]$ROOT,[string]$Msg) {
  $logDir = Join-Path (Join-Path $ROOT "system") "logs"
  if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
  $log = Join-Path $logDir "omega_doctor.log"
  Add-Content -Path $log -Value ("[{0}] {1}" -f (Get-Date).ToString("o"), $Msg) -Encoding utf8
}

function Backup-File([string]$ROOT,[string]$Abs,[string]$Tag) {
  $bdir = Join-Path (Join-Path $ROOT "system") ("backups\doctor\" + $Tag + "\" + (Get-Date -Format "yyyyMMdd_HHmmss"))
  New-Item -ItemType Directory -Force -Path $bdir | Out-Null
  if (Test-Path $Abs) { Copy-Item -Force $Abs (Join-Path $bdir ([IO.Path]::GetFileName($Abs) + ".bak")) | Out-Null }
  return $bdir
}

function Get-Templates() {
  $t = @{}

  # NOTE: this is @" ... "@ (NOT @' ... '@) so it won't break the installer
  $t["system\sync\publish_state.ps1"] = @"
param([Parameter(Mandatory)][string]`$ROOT)

`$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

Import-Module (Join-Path `$ROOT "system\governor\scf.psm1") -Force
Import-Module (Join-Path `$ROOT "system\meta\ucg\ucg.psm1") -Force

Assert-ScfRunAllowed -ROOT `$ROOT -Subsystem "state.publish"
`$run = Start-UcgRun -ROOT `$ROOT -Subsystem "state.publish" -Script `$PSCommandPath

try {
  Write-Host "State Publish - Running (hotfix)" -ForegroundColor Cyan

  `$out = Join-Path `$ROOT "system\sync\published_state.json"
  `$dir = Split-Path -Parent `$out
  if (-not (Test-Path `$dir)) { New-Item -ItemType Directory -Force -Path `$dir | Out-Null }

  `$payload = [ordered]@{
    ts   = (Get-Date).ToString("o")
    root = `$ROOT
    note = "publish scaffold (hotfix)"
    paths = @{
      system_map      = (Join-Path `$ROOT "system\map\system_map.json")
      discovery_state = (Join-Path `$ROOT "ingestion\discovery\discovery_state.json")
    }
  }

  `$payload | ConvertTo-Json -Depth 20 | Out-File -FilePath `$out -Encoding utf8

  Write-UcgEvent -ROOT `$ROOT -Type "state.publish.tick" -Data @{ status="ok"; out_path=`$out }
  Stop-UcgRun -ROOT `$ROOT -RunId `$run -Status "ok"
  Write-Host "Publish OK" -ForegroundColor Green
} catch {
  `$err = `$_.Exception.Message
  try { Write-UcgEvent -ROOT `$ROOT -Type "state.publish.tick" -Data @{ status="error"; error=`$err } } catch {}
  try { Stop-UcgRun -ROOT `$ROOT -RunId `$run -Status "error" -Error `$err } catch {}
  throw
}
"@

  return $t
}

function Repair-FromTemplate([string]$ROOT,[string]$Rel,[hashtable]$Tpl,[switch]$Apply) {
  if (-not $Tpl.ContainsKey($Rel)) { return $false }
  $abs = Join-Path $ROOT $Rel
  $bak = Backup-File -ROOT $ROOT -Abs $abs -Tag ("template_" + ($Rel -replace "[\\/:]","_"))
  $body = $Tpl[$Rel]
  [scriptblock]::Create($body) | Out-Null
  if ($Apply) { Write-Utf8NoBom -Path $abs -Content $body; Log $ROOT ("FIXED: " + $Rel + " backup=" + $bak) }
  else { Log $ROOT ("DRYRUN: would fix " + $Rel + " backup=" + $bak) }
  return $true
}

function Run-Omega([string]$ROOT) {
  $runOnce = Join-Path (Join-Path (Join-Path $ROOT "system") "tools") "omega_run_once.ps1"
  if (-not (Test-Path $runOnce)) { throw "Missing omega_run_once.ps1: $runOnce" }
  return (& $runOnce -ROOT $ROOT *>&1 | Out-String)
}

# --- main ---
$lock = Join-Path (Join-Path (Join-Path $ROOT "system") "meta\ucg") ".omega.doctor.lock"
$lk = Acquire-FileLock $lock
if (-not $lk) { Write-Host "Omega Doctor: already running (lock busy)." -ForegroundColor Yellow; exit 0 }

try {
  $tpl = Get-Templates
  Log $ROOT ("START: mode=" + $Mode + " apply=" + $Apply)

  if ($Mode -eq "scan") {
    $p = Join-Path $ROOT "system\sync\publish_state.ps1"
    if ((Test-Path $p) -and (Parse-Ok $p)) { Write-Host "SCAN OK" -ForegroundColor Green; exit 0 }
    Write-Host "SCAN FAIL: system\sync\publish_state.ps1" -ForegroundColor Red
    exit 2
  }

  $rel="system\sync\publish_state.ps1"
  $p=Join-Path $ROOT $rel
  if (-not (Test-Path $p) -or -not (Parse-Ok $p)) {
    [void](Repair-FromTemplate -ROOT $ROOT -Rel $rel -Tpl $tpl -Apply:$Apply)
  }

  $out = Run-Omega $ROOT
  Log $ROOT ("OMEGA_OUTPUT:`n" + $out.TrimEnd())
  Write-Host "Doctor finished. See system\logs\omega_doctor.log" -ForegroundColor Cyan

  if ($Mode -eq "loop") {
    while ($true) {
      $sleep = $IntervalSec + (Get-Random -Minimum 0 -Maximum ($JitterSec + 1))
      Start-Sleep -Seconds $sleep
      $out = Run-Omega $ROOT
      Log $ROOT ("OMEGA_OUTPUT:`n" + $out.TrimEnd())
    }
  }
} finally {
  try { $lk.Dispose() } catch {}
}