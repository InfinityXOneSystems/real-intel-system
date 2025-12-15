param([Parameter(Mandatory)][string]$ROOT)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

function Import-Maybe([string]$Path){ if(Test-Path $Path){ Import-Module $Path -Force; return $true }; return $false }
$scfOk = Import-Maybe (Join-Path $ROOT 'system\governor\scf.psm1')
$ucgOk = Import-Maybe (Join-Path $ROOT 'system\meta\ucg\ucg.psm1')

if($scfOk -and (Get-Command Assert-ScfRunAllowed -ErrorAction SilentlyContinue)){
  Assert-ScfRunAllowed -ROOT $ROOT -Subsystem 'builder'
}
if($ucgOk -and (Get-Command Initialize-Ucg -ErrorAction SilentlyContinue)){
  Initialize-Ucg -ROOT $ROOT
}

$run=$null
if($ucgOk -and (Get-Command Start-UcgRun -ErrorAction SilentlyContinue)){
  $run=Start-UcgRun -ROOT $ROOT -Subsystem 'builder' -Script $PSCommandPath
}

try {
  Write-Host 'Omega Builder - Running (hotfix)' -ForegroundColor Yellow

  $modules = @(
    'system\kernel',
    'system\builder',
    'system\upgrade',
    'system\map',
    'system\evolution',
    'system\meta\ucg',
    'system\governor',
    'system\sync',
    'ingestion\discovery',
    'agents\market'
  )

  $created = @()
  foreach($m in $modules){
    $p = Join-Path $ROOT $m
    if(-not (Test-Path $p)){
      New-Item -ItemType Directory -Force -Path $p | Out-Null
      $created += $m
    }
  }

  if($ucgOk -and (Get-Command Write-UcgEvent -ErrorAction SilentlyContinue)){
    Write-UcgEvent -ROOT $ROOT -Type 'builder.tick' -Data @{ status='ok'; created=$created }
  }
  if($ucgOk -and $run -and (Get-Command Stop-UcgRun -ErrorAction SilentlyContinue)){
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status 'ok'
  }

  Write-Host 'Builder OK' -ForegroundColor Green
} catch {
  $err=$_.Exception.Message
  if($ucgOk -and (Get-Command Write-UcgEvent -ErrorAction SilentlyContinue)){
    Write-UcgEvent -ROOT $ROOT -Type 'builder.tick' -Data @{ status='error'; error=$err }
  }
  if($ucgOk -and $run -and (Get-Command Stop-UcgRun -ErrorAction SilentlyContinue)){
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status 'error' -Error $err
  }
  throw
}