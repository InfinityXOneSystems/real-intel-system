param([string]$ROOT)

param([string]$ROOT)

Write-Host "Ã°Å¸Å¡â‚¬ OMEGA MASTER RUNNER V2 INIT" -ForegroundColor Magenta

& "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\kernel\omega_kernel.ps1"  -ROOT $ROOT
& "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\builder\omega_builder.ps1" -ROOT $ROOT
& "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\upgrade\omega_upgrade.ps1" -ROOT $ROOT
& "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\map\omega_map.ps1"     -ROOT $ROOT
& "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\evolution\omega_evolve.ps1"  -ROOT $ROOT

Write-Host "Ã¢Å“â€ OMEGA STACK V2 COMPLETE Ã¢â‚¬â€ System Autonomous." -ForegroundColor Green



