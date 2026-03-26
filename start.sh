#!/bin/bash

echo "========================================"
echo "  OpenClaw Multi-Agent Manager"
echo "  Starting Backend and Frontend..."
echo "========================================"
echo

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} uv is not installed. Please install it first."
    echo "Run: pip install uv"
    exit 1
fi

# Check if node is installed
if ! command -v node &> /dev/null; then
    echo -e "${RED}[ERROR]${NC} Node.js is not installed. Please install it first."
    exit 1
fi

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Install backend dependencies if needed
echo -e "${YELLOW}[1/4]${NC} Checking backend dependencies..."
cd backend
if [ ! -d ".venv" ]; then
    echo "Installing backend dependencies..."
    uv sync
fi
cd ..

# Install frontend dependencies if needed
echo -e "${YELLOW}[2/4]${NC} Checking frontend dependencies..."
cd frontend
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
cd ..

# Create logs directory
mkdir -p logs

# Start backend
echo -e "${YELLOW}[3/4]${NC} Starting backend server (port 3789)..."
cd backend
uv run uvicorn src.main:app --reload --port 3789 > ../logs/backend.log 2>&1 &
BACKEND_PID=$!
cd ..
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo -e "${YELLOW}[4/4]${NC} Starting frontend server (port 5173)..."
cd frontend
npm run dev > ../logs/frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..
echo "Frontend PID: $FRONTEND_PID"

# Save PIDs to file
echo "$BACKEND_PID" > logs/backend.pid
echo "$FRONTEND_PID" > logs/frontend.pid

echo
echo "========================================"
echo -e "${GREEN}Services started successfully!${NC}"
echo "  Backend:  http://localhost:3789"
echo "  Frontend: http://localhost:5173"
echo "  API Docs: http://localhost:3789/docs"
echo "========================================"
echo
echo "Logs are saved in ./logs/"
echo "To stop services, run: ./stop.sh"
echo

# Open browser (Linux)
if command -v xdg-open &> /dev/null; then
    sleep 2
    xdg-open http://localhost:5173 2>/dev/null &
fi

# Keep script running and show logs
echo "Press Ctrl+C to stop all services..."
trap "echo 'Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f logs/*.pid; exit 0" SIGINT SIGTERM

# Tail logs
tail -f logs/backend.log logs/frontend.log 2>/dev/null
