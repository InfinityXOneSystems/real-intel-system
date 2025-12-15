param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference = "Stop"
Set-StrictMode -Version Latest

$SYSTEM = Join-Path $ROOT "system"
$MASTER = Join-Path $SYSTEM "omega_master.ps1"

# Single-instance lock (file lock)
$lockPath = Join-Path (Join-Path $SYSTEM "meta\ucg") ".omega.run.lock"
$lockDir  = Split-Path -Parent $lockPath
if ($lockDir -and -not (Test-Path $lockDir)) { New-Item -ItemType Directory -Force -Path $lockDir | Out-Null }

$fs = $null
try {
  try {
    $fs = [System.IO.File]::Open($lockPath,
      [System.IO.FileMode]::OpenOrCreate,
      [System.IO.FileAccess]::ReadWrite,
      [System.IO.FileShare]::None
    )
  } catch [System.IO.IOException] {
    Write-Host "Omega already running (lock busy). Skipping." -ForegroundColor Yellow
    exit 0
  }

  if (-not (Test-Path $MASTER)) { throw "Missing omega_master.ps1: $MASTER" }

  Push-Location $ROOT
  try {
    & $MASTER -ROOT $ROOT
  } finally {
    Pop-Location
  }
} finally {
  if ($fs) { $fs.Dispose() }
}