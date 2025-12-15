param(
  [Parameter(Mandatory)][string]$ROOT,
  [int]$IntervalSec = 180,
  [int]$JitterSec   = 30
)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$SYSTEM = Join-Path $ROOT "system"
$MASTER = Join-Path $SYSTEM "omega_master.ps1"
$LOGDIR = Join-Path $SYSTEM "logs"
$LOG    = Join-Path $LOGDIR "omega_daemon.log"
$PAUSE  = Join-Path (Join-Path $SYSTEM "governor") "pause.flag"

if (-not (Test-Path $LOGDIR)) { New-Item -ItemType Directory -Force -Path $LOGDIR | Out-Null }

function Log([string]$msg) {
  $ts = (Get-Date).ToString("o")
  Add-Content -Path $LOG -Value "[$ts] $msg" -Encoding utf8
}

# Single-instance guard (prevents multiple background copies)
$mutexName = "Global\\InfinityXOS_OmegaDaemon"
$created = $false
$mutex = New-Object System.Threading.Mutex($true, $mutexName, [ref]$created)
if (-not $created) {
  Log "EXIT: another omega daemon is already running."
  exit 0
}

try {
  Log "START: Omega daemon online. ROOT=$ROOT IntervalSec=$IntervalSec JitterSec=$JitterSec"

  while ($true) {
    try {
      if (Test-Path $PAUSE) {
        Log "PAUSED: pause.flag present => skipping tick"
      } else {
        if (-not (Test-Path $MASTER)) {
          Log "ERROR: omega_master.ps1 missing: $MASTER"
        } else {
          Log "TICK: running omega_master.ps1"
          Push-Location $ROOT
          try {
            # Capture all output (stdout+stderr) into the daemon log
            $out = & $MASTER -ROOT $ROOT *>&1 | Out-String
            if ($out) { Log ("OMEGA_OUTPUT:
" + $out.TrimEnd()) }
            Log "TICK: omega_master OK"
          } finally {
            Pop-Location
          }
        }
      }
    } catch {
      Log ("TICK_ERROR: " + $_.Exception.Message)
    }

    $sleep = $IntervalSec + (Get-Random -Minimum 0 -Maximum ($JitterSec + 1))
    Start-Sleep -Seconds $sleep
  }
} finally {
  try { $mutex.ReleaseMutex() | Out-Null } catch {}
  $mutex.Dispose()
}