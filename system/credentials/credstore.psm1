Set-StrictMode -Version Latest

function Get-CredStorePath {
  $base = Join-Path $env:LOCALAPPDATA "InfinityXOne\CredentialManager"
  if (-not (Test-Path $base)) { New-Item -ItemType Directory -Force -Path $base | Out-Null }
  return $base
}

function Initialize-CredStore {
  $base = Get-CredStorePath
  $manifest = Join-Path $base "manifest.json"
  if (-not (Test-Path $manifest)) {
    @{ created=(Get-Date).ToString("o"); version="CREDSTORE_V1"; keys=@() } |
      ConvertTo-Json -Depth 10 | Out-File -FilePath $manifest -Encoding utf8
  }
}

function Set-InfinitySecret {
  param([Parameter(Mandatory)][string]$Name, [Parameter(Mandatory)][securestring]$Value)
  Initialize-CredStore
  $base = Get-CredStorePath
  $path = Join-Path $base ($Name + ".sec")
  $enc  = ConvertFrom-SecureString -SecureString $Value
  $enc | Out-File -FilePath $path -Encoding utf8

  $manifest = Join-Path $base "manifest.json"
  $m = (Get-Content -Raw -Path $manifest | ConvertFrom-Json)
  $keys = @($m.keys)
  if ($keys -notcontains $Name) { $keys += $Name }
  $m.keys = $keys
  $m.updated = (Get-Date).ToString("o")
  $m | ConvertTo-Json -Depth 10 | Out-File -FilePath $manifest -Encoding utf8
}

function Get-InfinitySecretPlain {
  param([Parameter(Mandatory)][string]$Name)
  Initialize-CredStore
  $base = Get-CredStorePath
  $path = Join-Path $base ($Name + ".sec")
  if (-not (Test-Path $path)) { return $null }
  $enc = Get-Content -Raw -Path $path
  $sec = ConvertTo-SecureString $enc
  $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($sec)
  try { return [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr) }
  finally { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr) }
}

Export-ModuleMember -Function *-Infinity*, Get-CredStorePath, Initialize-CredStore