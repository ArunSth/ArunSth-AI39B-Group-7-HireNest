#!/usr/bin/env pwsh
# Creates venv if missing, installs requirements once, activates and runs the app.
param()

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $root

$venv = Join-Path $root 'venv'
if (-not (Test-Path $venv)) {
    Write-Host "Creating virtual environment..."
    python -m venv venv
    & "$venv\Scripts\python.exe" -m pip install --upgrade pip
    if (Test-Path (Join-Path $root 'requirements.txt')) {
        Write-Host "Installing requirements..."
        & "$venv\Scripts\python.exe" -m pip install -r requirements.txt
    }
}

Write-Host "Activating virtualenv and starting app..."
& "$venv\Scripts\Activate.ps1"
python run.py