@echo off
setlocal
title Medical FactGuard AI - Backend Server

cd /d "%~dp0"

echo ==========================================
echo       Medical FactGuard AI
echo ==========================================
echo.

if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment was not found.
    echo Expected: %CD%\.venv\Scripts\python.exe
    echo.
    pause
    exit /b 1
)

echo Starting backend on http://127.0.0.1:8000
echo Keep this window OPEN while using the Chrome extension.
echo Auto-reload is disabled to avoid Windows reloader subprocess
echo failures and duplicate AI model loading.
echo.

".venv\Scripts\python.exe" -m uvicorn backend.api:app --host 127.0.0.1 --port 8000 --log-level info

echo.
echo [STOPPED] Backend server has exited.
echo Review the error above. This window will remain open.
pause
endlocal
