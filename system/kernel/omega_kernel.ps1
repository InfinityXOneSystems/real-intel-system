param([Parameter(Mandatory)][string]$ROOT)
$ErrorActionPreference="Stop"
Set-StrictMode -Version Latest

function Import-Maybe([string]$Path){ if(Test-Path $Path){ Import-Module $Path -Force; return $true }; return $false }
$scfOk = Import-Maybe (Join-Path $ROOT 'system\governor\scf.psm1')
$ucgOk = Import-Maybe (Join-Path $ROOT 'system\meta\ucg\ucg.psm1')

if($scfOk -and (Get-Command Assert-ScfRunAllowed -ErrorAction SilentlyContinue)){
  Assert-ScfRunAllowed -ROOT $ROOT -Subsystem 'kernel'
}
if($ucgOk -and (Get-Command Initialize-Ucg -ErrorAction SilentlyContinue)){
  Initialize-Ucg -ROOT $ROOT
}

$run=$null
if($ucgOk -and (Get-Command Start-UcgRun -ErrorAction SilentlyContinue)){
  $run=Start-UcgRun -ROOT $ROOT -Subsystem 'kernel' -Script $PSCommandPath
}

try {
  Write-Host '🔥 Omega Kernel — Running (hotfix)' -ForegroundColor Magenta
  $out = Join-Path $ROOT 'system\kernel\omega_reasoning.json'
  $payload = @{
    ts=(Get-Date).ToString('o')
    status='kernel operational'
    safe_mode=($env:INFINITY_SAFE_MODE -eq '1')
    note='hotfix kernel: parse-safe, UCG wired'
  }
  $payload | ConvertTo-Json -Depth 20 | Out-File -FilePath $out -Encoding utf8 -Force

  if($ucgOk -and (Get-Command Write-UcgEvent -ErrorAction SilentlyContinue)){
    Write-UcgEvent -ROOT $ROOT -Type 'kernel.tick' -Data @{ status='ok'; out_path=$out }
  }
  if($ucgOk -and $run -and (Get-Command Stop-UcgRun -ErrorAction SilentlyContinue)){
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status 'ok'
  }
  Write-Host '✔ Kernel OK' -ForegroundColor Green
} catch {
  $err=$_.Exception.Message
  if($ucgOk -and (Get-Command Write-UcgEvent -ErrorAction SilentlyContinue)){
    Write-UcgEvent -ROOT $ROOT -Type 'kernel.tick' -Data @{ status='error'; error=$err }
  }
  if($ucgOk -and $run -and (Get-Command Stop-UcgRun -ErrorAction SilentlyContinue)){
    Stop-UcgRun -ROOT $ROOT -RunId $run -Status 'error' -Error $err
  }
  throw
}