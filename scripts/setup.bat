@echo off
REM Setup script for Interactive Agent Playground with uv (Windows)

echo.
echo 🚀 Setting up Interactive Agent Playground environment with uv...
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ❌ Error: uv is not installed
    echo Install from: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

for /f "tokens=*" %%i in ('uv --version') do set UV_VERSION=%%i
echo ✓ uv found: %UV_VERSION%

REM Create Python 3.11 virtual environment
echo.
echo 📦 Creating virtual environment with Python 3.11...
call uv venv --python 3.11 .venv

REM Activate virtual environment
if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
    echo ✓ Virtual environment activated
) else (
    echo ⚠ Could not find activation script
)

REM Install dependencies
echo.
echo 📥 Installing dependencies...
call uv pip install -r requirements.txt

REM Install development dependencies
echo.
echo 🔧 Installing development tools...
call uv pip install ^
    mypy>=1.0 ^
    black>=23.0 ^
    ruff>=0.1

REM Optional: Install Ollama support
echo.
echo Optional: For Ollama integration, run:
echo   uv pip install requests>=2.31.0

echo.
echo ✅ Setup complete!
echo.
echo Usage:
echo   Activate environment:  .venv\Scripts\activate.bat (Windows)
echo   Run script:            python interactive_agent.py
echo   Deactivate:            deactivate
echo.
pause
