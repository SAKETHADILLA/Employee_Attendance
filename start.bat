@echo off
setlocal
title Employee Attendance and Analytics API
color 0A

echo ============================================================
echo   Employee Attendance and Analytics API - Starting Service
echo ============================================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.11+ and ensure it is added to your PATH.
    echo.
    pause
    exit /b 1
)

if exist .venv\Scripts\activate.bat (
    echo [*] Activating virtual environment .venv
    call .venv\Scripts\activate.bat
)

if exist venv\Scripts\activate.bat (
    echo [*] Activating virtual environment venv
    call venv\Scripts\activate.bat
)

if exist .env (
    echo [*] Database Configuration: Loading from .env file
) else (
    if not defined MONGO_URI (
        set MONGO_URI=mongodb://localhost:27017
    )
    if not defined MONGO_DB (
        set MONGO_DB=attendance_db
    )
    echo [*] Target Database URI : %MONGO_URI%
    echo [*] Database Name       : %MONGO_DB%
)
echo [*] API Port            : 8000
echo [*] Interactive Docs    : http://localhost:8000/docs
echo [*] Health Check        : http://localhost:8000/health
echo.
echo [*] Starting Uvicorn server with hot reload
echo Press CTRL+C to stop the server at any time.
echo.

python -m uvicorn app.main:app --port 8000 --reload

pause
