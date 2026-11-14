@echo off
REM ==============================================================================
REM CircuitRF M365 Copilot Agent Bridge Server (Windows Work PC Launcher)
REM ==============================================================================

echo [INFO] Starting CircuitRF Microsoft 365 Copilot Agent Bridge...
cd /d "%~dp0\.."

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not found in PATH. Please install Python 3.10+ and add to PATH.
    pause
    exit /b 1
)

REM Check or create virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Creating Python virtual environment in venv...
    python -m venv venv
    call venv\Scripts\activate.bat
    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt
) else (
    call venv\Scripts\activate.bat
)

REM Set environment variables
set HOST=127.0.0.1
set PORT=8000

echo [INFO] CircuitRF MCP Bridge starting on http://%HOST%:%PORT%
echo [INFO] Swagger Docs available at http://%HOST%:%PORT%/docs
echo [INFO] Press Ctrl+C to terminate.

python -m uvicorn bridge_server.server:app --host %HOST% --port %PORT% --reload
pause
