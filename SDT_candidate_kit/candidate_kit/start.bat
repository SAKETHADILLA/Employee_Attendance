@echo off
title Employee Attendance & Analytics API
color 0A

echo ============================================================
echo   Employee Attendance & Analytics API - Starting Service
echo ============================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.11+ and ensure it is added to your PATH.
    echo.
    pause
    exit /b 1
)

:: 2. Activate virtual environment if present
if exist .venv\Scripts\activate.bat (
    echo [*] Activating virtual environment (.venv)...
    call .venv\Scripts\activate.bat
) else if exist venv\Scripts\activate.bat (
    echo [*] Activating virtual environment (venv)...
    call venv\Scripts\activate.bat
)

:: 3. Set default MongoDB environment variables if not already defined
if "%MONGO_URI%"=="" (
    set MONGO_URI=mongodb://localhost:27017
)
if "%MONGO_DB%"=="" (
    set MONGO_DB=attendance_db
)

echo [*] Target Database URI : %MONGO_URI%
echo [*] Database Name       : %MONGO_DB%
echo [*] API Port            : 8000
echo [*] Interactive Docs    : http://localhost:8000/docs
echo [*] Health Check        : http://localhost:8000/health
echo.
echo [*] Starting Uvicorn server with hot reload...
echo Press CTRL+C to stop the server at any time.
echo.

:: 4. Start the application
python -m uvicorn app.main:app --port 8000 --reload

if %errorlevel% neq 0 (
    echo.
    echo [!] Server stopped or exited with error code %errorlevel%.
    pause
)
