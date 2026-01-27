#!/usr/bin/env pwsh
# Start frontend development server
Set-Location $PSScriptRoot
Write-Host "Starting frontend server from: $PWD" -ForegroundColor Cyan
npm start
