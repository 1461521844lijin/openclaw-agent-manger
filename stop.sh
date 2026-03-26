#!/bin/bash

echo "========================================"
echo "  Stopping OpenClaw Manager Services"
echo "========================================"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Read PIDs and kill processes
if [ -f logs/backend.pid ]; then
    BACKEND_PID=$(cat logs/backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        kill $BACKEND_PID
        echo "Backend stopped (PID: $BACKEND_PID)"
    fi
    rm -f logs/backend.pid
fi

if [ -f logs/frontend.pid ]; then
    FRONTEND_PID=$(cat logs/frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        kill $FRONTEND_PID
        echo "Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm -f logs/frontend.pid
fi

# Kill any remaining processes on ports
if command -v lsof &> /dev/null; then
    BACKEND_PORT=$(lsof -ti:3789 2>/dev/null)
    if [ ! -z "$BACKEND_PORT" ]; then
        kill $BACKEND_PORT 2>/dev/null
        echo "Killed process on port 3789"
    fi

    FRONTEND_PORT=$(lsof -ti:5173 2>/dev/null)
    if [ ! -z "$FRONTEND_PORT" ]; then
        kill $FRONTEND_PORT 2>/dev/null
        echo "Killed process on port 5173"
    fi
fi

echo "All services stopped."
