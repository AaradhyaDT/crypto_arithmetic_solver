# Activate the Python virtual environment for this project.
# Usage: .\tools\activate_venv.ps1

$venvPath = Join-Path $PSScriptRoot '..\.venv\Scripts\Activate.ps1'
if (-Not (Test-Path $venvPath)) {
    Write-Error "Virtual environment activation script not found at $venvPath"
    exit 1
}

Write-Host "Activating .venv..." -ForegroundColor Green
. $venvPath
Write-Host "Activated .venv. Run your Python commands now." -ForegroundColor Green
