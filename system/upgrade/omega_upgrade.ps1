param([Parameter(Mandatory)][string]$ROOT)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

function Import-Maybe([string]$Path){ if(Test-Path $Path){ Import-Module $Path -Force; return $true }; return $false }
$scfOk = Import-Maybe (Join-Path $ROOT 'system\governor\scf.psm1')
$ucgOk = Import-Maybe (Join-Path $ROOT 'system\meta\ucg\ucg.psm1')

if($scfOk -and (Get-Command Assert-ScfRunAllowed -ErrorAction SilentlyContinue)){
  Assert-ScfRunAllowed -ROOT $ROOT -Subsystem 'upgrade'
}
if($ucgOk -and (Get-Command Initialize-Ucg -ErrorAction SilentlyContinue)){
  Initialize-Ucg -ROOT $ROOT
}

$run=$null
if($ucgOk -and (Get-Command Start-UcgRun -ErrorAction SilentlyContinue)){
  $run=Start-UcgRun -ROOT $ROOT -Subsystem 'upgrade' -Script $PSCommandPath
}

try {
  Write-Host 'Omega Upgrade - Running (hotfix)' -ForegroundColor Yellow

  # non-destructive policy: recommend/plan only
  $actions = @(
    'scan_deprecations',
    'recommend_migrations',
    'validate_structure',
    'enforce_non_destructive'
  )

  $modeObj = $null
  if($scfOk -and (Get-Command Get-ScfMode -ErrorAction SilentlyContinue)){
    $modeObj = Get-ScfMode -ROOT $ROOT
  }

  $payload = @{ status='ok'; actions=$actions; mode=$(if($modeObj){$modeObj.mode}else{'unknown'}) }
  if($ucgOk -and (Get-Command Write-UcgEvent -ErrorAction SilentlyContinue)){
    Write-UcgEvent -ROOT $ROOT -Type 'upgrade.tick' -Data $payload
  }
  if($ucgOk -and $run -and (Get-Command Stop-UcgRun -ErrorAction SilentlyContinue)){
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status 'ok'
  }

  Write-Host 'Upgrade OK' -ForegroundColor Green
} catch {
  $err=$_.Exception.Message
  if($ucgOk -and (Get-Command Write-UcgEvent -ErrorAction SilentlyContinue)){
    Write-UcgEvent -ROOT $ROOT -Type 'upgrade.tick' -Data @{ status='error'; error=$err }
  }
  if($ucgOk -and $run -and (Get-Command Stop-UcgRun -ErrorAction SilentlyContinue)){
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status 'error' -Error $err
  }
  throw
}