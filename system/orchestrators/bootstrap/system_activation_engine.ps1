param([string]$ROOT)

param([string]$ROOT)

Write-Host '--- INFINITY XOS ACTIVATION ENGINE STARTING ---' -ForegroundColor Cyan

# Start Services
foreach (\ in [
    "taxonomy-service",
    "todo-service",
    "index-service",
    "builder-service",
    "doc-service",
    "cortex-service",
    "validator-service",
    "deploy-service"
]) {
    Write-Host "Launching service: \" -ForegroundColor Yellow
}

Write-Host 'Starting Repo Sync Engine...' -ForegroundColor Yellow
powershell -ExecutionPolicy Bypass -File "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\orchestrators\bootstrap\repo_sync_engine_v3.ps1"

Write-Host 'Starting Auto-Evolve Kernel...' -ForegroundColor Magenta
powershell -ExecutionPolicy Bypass -File "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\orchestrators\evolution\auto_evolve_kernel.ps1"

Write-Host 'Starting Diagnostics...' -ForegroundColor DarkCyan
powershell -ExecutionPolicy Bypass -File "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\orchestrators\diagnostics\predictive_watchdog.ps1"
powershell -ExecutionPolicy Bypass -File "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\orchestrators\diagnostics\health_check.ps1"
powershell -ExecutionPolicy Bypass -File "C:\Users\JARVIS\OneDrive\Documents\InfinityXOneSystems\system\orchestrators\diagnostics\self_healing.ps1"

Write-Host '--- INFINITY XOS FULLY ONLINE ---' -ForegroundColor Green



