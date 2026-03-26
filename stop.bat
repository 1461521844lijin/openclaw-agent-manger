@echo off
chcp 65001 >nul
echo ========================================
echo   Stopping OpenClaw Manager Services
echo ========================================
echo.

:: Kill processes on ports
echo Stopping backend (port 3789)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3788 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>nul
)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :3789 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>nul
)

echo Stopping frontend (port 5173)...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>nul
)

:: Kill any node and python processes that might be running
taskkill /F /FI "WINDOWTITLE eq OpenClaw Backend*" >nul 2>nul
taskkill /F /FI "WINDOWTITLE eq OpenClaw Frontend*" >nul 2>nul

echo.
echo All services stopped.
pause
