param([Parameter(Mandatory)][string]$ROOT)

$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

Import-Module (Join-Path $ROOT "system\governor\scf.psm1") -Force
Import-Module (Join-Path $ROOT "system\meta\ucg\ucg.psm1") -Force

# credstore is optional (only used if present)
$cred = Join-Path $ROOT "system\credentials\credstore.psm1"
if (Test-Path $cred) { Import-Module $cred -Force }

Assert-ScfRunAllowed -ROOT $ROOT -Subsystem "repo.sync"
$run = Start-UcgRun -ROOT $ROOT -Subsystem "repo.sync" -Script $PSCommandPath

try {
  $safe = ($env:INFINITY_SAFE_MODE -eq "1")
  if ($safe) {
    Write-Host "Repo Sync - SKIP (safe mode on)" -ForegroundColor Yellow
    Write-UcgEvent -ROOT $ROOT -Type "repo.sync.tick" -Data @{ status="skipped"; reason="safe_mode" }
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"
    return
  }

  $profilePath = Join-Path $ROOT "system\config\infinity_profile.json"
  if (-not (Test-Path $profilePath)) { throw "Missing profile: $profilePath" }

  $profile = Get-Content -Raw -Path $profilePath | ConvertFrom-Json
  $org  = $profile.identity.github_org
  $reposDir = $profile.paths.repositories_dir

  if (-not $org) { throw "Profile missing identity.github_org" }
  if (-not $reposDir) { $reposDir = (Join-Path $ROOT "Repositories") }

  if (-not (Test-Path $reposDir)) { New-Item -ItemType Directory -Force -Path $reposDir | Out-Null }

  Write-Host ("Repo Sync - Org: {0} => {1}" -f $org, $reposDir) -ForegroundColor Cyan

  $names = @()

  # Prefer GitHub CLI
  $gh = Get-Command gh -ErrorAction SilentlyContinue
  if ($gh) {
    try {
      $json = gh repo list $org --limit 500 --json name 2>$null
      if ($json) {
        $parsed = $json | ConvertFrom-Json
        $names = @($parsed | ForEach-Object { $_.name })
      }
    } catch {}
  }

  # Fallback REST
  if (-not $names -or $names.Count -eq 0) {
    $token = $env:GITHUB_TOKEN
    if (-not $token -and (Get-Command Get-InfinitySecretPlain -ErrorAction SilentlyContinue)) {
      $token = Get-InfinitySecretPlain -Name "github_pat"
    }
    if (-not $token) { throw "Repo Sync needs gh auth OR GITHUB_TOKEN OR credstore github_pat." }

    $headers = @{ Authorization = ("token " + $token); "User-Agent"="InfinityXOS" }
    $page = 1
    while ($true) {
      $url = "https://api.github.com/orgs/$org/repos?per_page=100&page=$page"
      $resp = Invoke-RestMethod -Uri $url -Headers $headers -Method Get
      if (-not $resp -or $resp.Count -eq 0) { break }
      $names += @($resp | ForEach-Object { $_.name })
      $page++
      if ($page -gt 50) { break }
    }
  }

  if (-not $names -or $names.Count -eq 0) { throw ("No repos discovered for org '{0}'." -f $org) }

  $synced = 0
  foreach ($r in $names) {
    $dest = Join-Path $reposDir $r
    if (-not (Test-Path $dest)) {
      Write-Host ("Cloning: {0}" -f $r) -ForegroundColor Yellow
      git clone ("https://github.com/$org/$r.git") $dest | Out-Null
    } else {
      Write-Host ("Pulling: {0}" -f $r) -ForegroundColor DarkGray
      git -C $dest pull | Out-Null
    }
    $synced++
  }

  $logPath = Join-Path $reposDir "sync_log.txt"
  ("[{0}] synced={1}" -f (Get-Date -Format o), $synced) | Out-File -FilePath $logPath -Append -Encoding utf8

  Write-UcgEvent -ROOT $ROOT -Type "repo.sync.tick" -Data @{ status="ok"; repos=$synced; repos_dir=$reposDir }
  Stop-UcgRun -ROOT $ROOT -RunId $run -Status "ok"

  Write-Host ("Repo Sync complete ({0} repos)." -f $synced) -ForegroundColor Green
} catch {
  $err = $_.Exception.Message
  try { Write-UcgEvent -ROOT $ROOT -Type "repo.sync.tick" -Data @{ status="error"; error=$err } } catch {}
  try { Stop-UcgRun -ROOT $ROOT -RunId $run -Status "error" -Error $err } catch {}
  throw
}