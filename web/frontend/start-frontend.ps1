# Start frontend development server
Set-Location $PSScriptRoot
$env:NODE_OPTIONS = '--no-warnings'
$env:BROWSER = 'none'
$env:TSC_COMPILE_ON_ERROR = 'true'
$env:ESLINT_NO_DEV_ERRORS = 'true'
npm start
