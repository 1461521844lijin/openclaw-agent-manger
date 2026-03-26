@echo off
chcp 65001 >nul
echo ========================================
echo   OpenClaw Multi-Agent Manager
echo   Starting Backend and Frontend...
echo ========================================
echo.

:: Check if uv is installed
where uv >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] uv is not installed. Please install it first.
    echo Run: pip install uv
    pause
    exit /b 1
)

:: Check if node is installed
where node >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed. Please install it first.
    pause
    exit /b 1
)

:: Install backend dependencies if needed
echo [1/4] Checking backend dependencies...
cd backend
if not exist ".venv" (
    echo Installing backend dependencies...
    uv sync
)
cd ..

:: Install frontend dependencies if needed
echo [2/4] Checking frontend dependencies...
cd frontend
if not exist "node_modules" (
    echo Installing frontend dependencies...
    call npm install
)
cd ..

:: Start backend
echo [3/4] Starting backend server (port 3789)...
start "OpenClaw Backend" cmd /k "cd backend && uv run uvicorn src.main:app --reload --port 3789"

:: Wait for backend to start
timeout /t 3 /nobreak >nul

:: Start frontend
echo [4/4] Starting frontend server (port 5173)...
start "OpenClaw Frontend" cmd /k "cd frontend && npm run dev"

echo.
echo ========================================
echo   Services started successfully!
echo   Backend:  http://localhost:3789
echo   Frontend: http://localhost:5173
echo   API Docs: http://localhost:3789/docs
echo ========================================
echo.
echo Press any key to open browser...
pause >nul

:: Open browser
start http://localhost:5173
