#!/usr/bin/env pwsh
# Start backend server in dedicated window
Set-Location $PSScriptRoot
Write-Host "Starting backend server from: $PWD" -ForegroundColor Cyan
python -m uvicorn main:app --host 0.0.0.0 --port 8000
