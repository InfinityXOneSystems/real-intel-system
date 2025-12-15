Set-StrictMode -Version Latest

function Get-ScfPaths {
  param([Parameter(Mandatory)][string]$ROOT)
  $base = Join-Path $ROOT "system\governor"
  return @{
    Base     = $base
    Mode     = (Join-Path $base "mode.json")
    Policies = (Join-Path $base "policies.json")
    Lock     = (Join-Path $base ".scf.lock")
  }
}

function Invoke-WithScfLock {
  param([Parameter(Mandatory)][string]$LockPath, [Parameter(Mandatory)][scriptblock]$Action)
  $fs = [System.IO.File]::Open($LockPath, [System.IO.FileMode]::OpenOrCreate, [System.IO.FileAccess]::ReadWrite, [System.IO.FileShare]::None)
  try { return & $Action } finally { $fs.Dispose() }
}

function Initialize-Scf {
  param([Parameter(Mandatory)][string]$ROOT)
  $p = Get-ScfPaths -ROOT $ROOT
  if (-not (Test-Path $p.Base)) { New-Item -ItemType Directory -Force -Path $p.Base | Out-Null }

  if (-not (Test-Path $p.Mode)) {
    @{
      mode="normal"
      updated=(Get-Date).ToString("o")
      budgets=@{
        max_files_changed_per_tick=250
        max_disk_mb_per_tick=512
      }
      flags=@{
        safe_mode=$false
        network_ingest=$true
        destructive_ops=$false
      }
    } | ConvertTo-Json -Depth 10 | Out-File -FilePath $p.Mode -Encoding utf8
  }

  if (-not (Test-Path $p.Policies)) {
    @{
      version="SCF_v1"
      policies=@(
        @{ name="default_no_destructive"; when=@{ mode=@("normal","safe") }; enforce=@{ destructive_ops=$false } },
        @{ name="safe_mode_blocks_network"; when=@{ mode=@("safe") }; enforce=@{ network_ingest=$false; safe_mode=$true } },
        @{ name="halt_all"; when=@{ mode=@("halt") }; enforce=@{ halt=$true } }
      )
    } | ConvertTo-Json -Depth 20 | Out-File -FilePath $p.Policies -Encoding utf8
  }
}

function Get-ScfMode {
  param([Parameter(Mandatory)][string]$ROOT)
  Initialize-Scf -ROOT $ROOT
  $p = Get-ScfPaths -ROOT $ROOT
  return (Get-Content -Raw -Path $p.Mode | ConvertFrom-Json)
}

function Set-ScfMode {
  param([Parameter(Mandatory)][string]$ROOT, [Parameter(Mandatory)][ValidateSet("normal","safe","halt")][string]$Mode)
  Initialize-Scf -ROOT $ROOT
  $p = Get-ScfPaths -ROOT $ROOT
  Invoke-WithScfLock -LockPath $p.Lock -Action {
    $m = (Get-Content -Raw -Path $p.Mode | ConvertFrom-Json)
    $m.mode = $Mode
    $m.updated = (Get-Date).ToString("o")
    $m | ConvertTo-Json -Depth 10 | Out-File -FilePath $p.Mode -Encoding utf8
  } | Out-Null
}

function Assert-ScfRunAllowed {
  param([Parameter(Mandatory)][string]$ROOT, [Parameter(Mandatory)][string]$Subsystem)
  $m = Get-ScfMode -ROOT $ROOT
  if ($m.mode -eq "halt") {
    Write-Host "🛑 SCF HALT: '$Subsystem' blocked (mode=halt)" -ForegroundColor Red
    exit 2
  }
  if ($m.mode -eq "safe" -or ($m.flags.safe_mode -eq $true)) { $env:INFINITY_SAFE_MODE="1" } else { $env:INFINITY_SAFE_MODE="0" }
}

Export-ModuleMember -Function *-Scf*, Assert-ScfRunAllowed