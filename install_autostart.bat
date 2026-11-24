bat
@echo off
title Medical FactGuard AI Server

cd /d C:\Projects\Medical-FactGuard-AI

echo ==========================================
echo       Medical FactGuard AI
echo ==========================================
echo.

echo Checking port 8000...

REM Check whether port 8000 is already occupied
netstat -ano | findstr /R /C:":8000 .*LISTENING" >nul

if %errorlevel%==0 (
    echo.
    echo ERROR: Port 8000 is already in use.
    echo Please stop the existing server first.
    echo.
    pause
    exit /b 1
)

echo Starting Medical FactGuard AI...
echo Auto-reload is ENABLED.
echo.

call .venv\Scripts\activate.bat

python -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause