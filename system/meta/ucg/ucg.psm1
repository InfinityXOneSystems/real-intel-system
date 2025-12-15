function Write-UcgEventsLine {
  param(
    [Parameter(Mandatory)][string]$EventsPath,
    [Parameter(Mandatory)][string]$Line
  )

  # NEVER crash omega because logging was locked.
  $mutexName = "Global\InfinityXOS_UcgEvents"
  $created = $false
  $mutex = New-Object System.Threading.Mutex($false, $mutexName, [ref]$created)
  $acquired = $false

  try {
    $acquired = $mutex.WaitOne([TimeSpan]::FromSeconds(30))
    if (-not $acquired) { return }

    $attempts = 40
    for ($i=0; $i -lt $attempts; $i++) {
      try {
        $dir = Split-Path -Parent $EventsPath
        if ($dir -and -not (Test-Path $dir)) { New-Item -ItemType Directory -Force -Path $dir | Out-Null }

        $fs = [System.IO.File]::Open($EventsPath, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
        try {
          $enc = New-Object System.Text.UTF8Encoding($false)
          $sw = New-Object System.IO.StreamWriter($fs, $enc)
          try {
            $sw.WriteLine($Line)
            $sw.Flush()
          } finally { $sw.Dispose() }
        } finally { $fs.Dispose() }

        return
      } catch [System.IO.IOException] {
        Start-Sleep -Milliseconds (50 + ($i * 50))
      } catch {
        return
      }
    }

    # fallback log if it still fails (still non-fatal)
    try {
      $fallback = $EventsPath + ".fallback"
      $fs2 = [System.IO.File]::Open($fallback, [System.IO.FileMode]::Append, [System.IO.FileAccess]::Write, [System.IO.FileShare]::ReadWrite)
      try {
        $enc2 = New-Object System.Text.UTF8Encoding($false)
        $sw2 = New-Object System.IO.StreamWriter($fs2, $enc2)
        try { $sw2.WriteLine($Line); $sw2.Flush() } finally { $sw2.Dispose() }
      } finally { $fs2.Dispose() }
    } catch {}
  } finally {
    if ($acquired) { try { $mutex.ReleaseMutex() | Out-Null } catch {} }
    $mutex.Dispose()
  }
}

Set-StrictMode -Version Latest

function Get-UcgPaths {
  param([Parameter(Mandatory)][string]$ROOT)
  $base = Join-Path $ROOT "system\meta\ucg"
  return @{
    Base   = $base
    Graph  = (Join-Path $base "graph.json")
    Events = (Join-Path $base "events.jsonl")
    Lock   = (Join-Path $base ".ucg.lock")   # DIRECTORY lock
    Schema = (Join-Path $base "schema.json")
    Stats  = (Join-Path $base "stats.json")
  }
}

function Acquire-UcgLock {
  param(
    [Parameter(Mandatory)][string]$LockDir,
    [int]$TimeoutMs = 60000,
    [int]$StaleSeconds = 120
  )
  $sw = [System.Diagnostics.Stopwatch]::StartNew()
  while ($true) {
    try {
      New-Item -ItemType Directory -Path $LockDir -ErrorAction Stop | Out-Null
      $metaPath = Join-Path $LockDir "meta.json"
      @{ pid = $PID; ts = (Get-Date).ToString("o") } | ConvertTo-Json -Compress |
        Out-File -FilePath $metaPath -Encoding utf8 -Force
      return
    } catch {
      $metaPath = Join-Path $LockDir "meta.json"
      if (Test-Path $metaPath) {
        try {
          $m = Get-Content -Raw -Path $metaPath | ConvertFrom-Json
          $age  = (Get-Date) - [datetime]$m.ts
          $proc = Get-Process -Id $m.pid -ErrorAction SilentlyContinue
          if (-not $proc -and $age.TotalSeconds -ge $StaleSeconds) {
            Remove-Item -Recurse -Force -Path $LockDir -ErrorAction SilentlyContinue
            Start-Sleep -Milliseconds 200
            continue
          }
        } catch { }
      }
      if ($sw.ElapsedMilliseconds -ge $TimeoutMs) { throw "UCG lock timeout: $LockDir" }
      Start-Sleep -Milliseconds 200
    }
  }
}

function Release-UcgLock {
  param([Parameter(Mandatory)][string]$LockDir)
  Remove-Item -Recurse -Force -Path $LockDir -ErrorAction SilentlyContinue
}

function Invoke-WithFileLock {
  param(
    [Parameter(Mandatory)][string]$LockPath,
    [Parameter(Mandatory)][scriptblock]$Action,
    [int]$TimeoutMs = 60000
  )
  Acquire-UcgLock -LockDir $LockPath -TimeoutMs $TimeoutMs | Out-Null
  try { return & $Action }
  finally { Release-UcgLock -LockDir $LockPath | Out-Null }
}

function Initialize-Ucg {
  param([Parameter(Mandatory)][string]$ROOT)
  $p = Get-UcgPaths -ROOT $ROOT
  if (-not (Test-Path $p.Base)) { New-Item -ItemType Directory -Force -Path $p.Base | Out-Null }

  Invoke-WithFileLock -LockPath $p.Lock -Action {
    if (-not (Test-Path $p.Graph)) {
      $g = @{
        version = "UCG_v1"
        created = (Get-Date).ToString("o")
        nodes   = @{}
        edges   = @()
      }
      $g | ConvertTo-Json -Depth 20 | Out-File -FilePath $p.Graph -Encoding utf8 -Force
    }
    if (-not (Test-Path $p.Events)) { New-Item -ItemType File -Force -Path $p.Events | Out-Null }
    if (-not (Test-Path $p.Stats)) {
      @{ last_compact = $null; events = 0; nodes = 0; edges = 0 } |
        ConvertTo-Json -Depth 8 | Out-File -FilePath $p.Stats -Encoding utf8 -Force
    }
  } | Out-Null
}

function Read-UcgGraph {
  param([Parameter(Mandatory)][string]$ROOT)
  $p = Get-UcgPaths -ROOT $ROOT
  Initialize-Ucg -ROOT $ROOT
  return (Get-Content -Raw -Path $p.Graph | ConvertFrom-Json)
}

function Write-UcgGraph {
  param([Parameter(Mandatory)][string]$ROOT, [Parameter(Mandatory)]$Graph)
  $p = Get-UcgPaths -ROOT $ROOT
  Invoke-WithFileLock -LockPath $p.Lock -Action {
    $Graph | ConvertTo-Json -Depth 20 | Out-File -FilePath $p.Graph -Encoding utf8 -Force
  } | Out-Null
}

function Write-UcgEvent {
  param(
    [Parameter(Mandatory)][string]$ROOT,
    [Parameter(Mandatory)][string]$Type,
    [Parameter(Mandatory)][hashtable]$Data
  )
  $p = Get-UcgPaths -ROOT $ROOT
  Initialize-Ucg -ROOT $ROOT
  $evt  = @{ ts=(Get-Date).ToString("o"); type=$Type; data=$Data }
  $line = ($evt | ConvertTo-Json -Depth 20 -Compress)
  Invoke-WithFileLock -LockPath $p.Lock -Action {
    Write-UcgEventsLine -EventsPath $p.Events -Line $line
  } | Out-Null
}

function Upsert-UcgNode {
  param(
    [Parameter(Mandatory)][string]$ROOT,
    [Parameter(Mandatory)][string]$Id,
    [Parameter(Mandatory)][string]$Kind,
    [hashtable]$Props = @{}
  )
  $p = Get-UcgPaths -ROOT $ROOT
  Initialize-Ucg -ROOT $ROOT

  Invoke-WithFileLock -LockPath $p.Lock -Action {
    $g = (Get-Content -Raw -Path $p.Graph | ConvertFrom-Json)

    if (-not $g.nodes) {
      $g | Add-Member -NotePropertyName nodes -NotePropertyValue ([pscustomobject]@{}) -Force
    }

    $node = @{
      id    = $Id
      kind  = $Kind
      ts    = (Get-Date).ToString("o")
      props = $Props
    }

    # IMPORTANT: keys like "run:xxxx" contain ":" -> must use Add-Member, not $obj.$key
    $g.nodes | Add-Member -NotePropertyName $Id -NotePropertyValue $node -Force

    $g | ConvertTo-Json -Depth 30 | Out-File -FilePath $p.Graph -Encoding utf8 -Force
  } | Out-Null
}function Add-UcgEdge {
  param(
    [Parameter(Mandatory)][string]$ROOT,
    [Parameter(Mandatory)][string]$From,
    [Parameter(Mandatory)][string]$To,
    [Parameter(Mandatory)][string]$Type,
    [hashtable]$Meta = @{}
  )
  $p = Get-UcgPaths -ROOT $ROOT
  Initialize-Ucg -ROOT $ROOT
  Invoke-WithFileLock -LockPath $p.Lock -Action {
    $g = (Get-Content -Raw -Path $p.Graph | ConvertFrom-Json)
    if (-not $g.edges) { $g | Add-Member -NotePropertyName edges -NotePropertyValue @() -Force }
    $g.edges = @($g.edges) + @(@{ from=$From; to=$To; type=$Type; ts=(Get-Date).ToString("o"); meta=$Meta })
    $g | ConvertTo-Json -Depth 20 | Out-File -FilePath $p.Graph -Encoding utf8 -Force
  } | Out-Null
}

function Start-UcgRun {
  param(
    [Parameter(Mandatory)][string]$ROOT,
    [Parameter(Mandatory)][string]$Subsystem,
    [string]$Script = $null
  )
  $runId = ([Guid]::NewGuid().ToString("n"))
  Upsert-UcgNode -ROOT $ROOT -Id ("run:" + $runId) -Kind "run" -Props @{ subsystem=$Subsystem; script=$Script; status="started" }
  Write-UcgEvent -ROOT $ROOT -Type "run.started" -Data @{ run_id=$runId; subsystem=$Subsystem; script=$Script }
  return $runId
}

function Stop-UcgRun {
  param(
    [Parameter(Mandatory)][string]$ROOT,
    [Parameter(Mandatory)][string]$RunId,
    [Parameter(Mandatory)][string]$Status,
    [string]$Error = $null
  )
  Upsert-UcgNode -ROOT $ROOT -Id ("run:" + $RunId) -Kind "run" -Props @{ status=$Status; error=$Error }
  Write-UcgEvent -ROOT $ROOT -Type "run.stopped" -Data @{ run_id=$RunId; status=$Status; error=$Error }
}

Export-ModuleMember -Function *-Ucg*, Invoke-WithFileLock, Get-UcgPaths, Initialize-Ucg
