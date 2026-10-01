#!/usr/bin/env bash
# Startup script for Multi-Agent Lead Generation System
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export PATH="/usr/local/bin:/Users/indianic/.nvm/versions/node/v20.20.1/bin:$PATH"

echo "=========================================================="
echo " Starting Multi-Agent Lead Generation & Proposal System   "
echo "=========================================================="

# 1. Start Backend FastAPI Server
echo "-> Starting Backend API server on http://localhost:8000..."
cd "$SCRIPT_DIR/backend"
"$SCRIPT_DIR/.venv/bin/uvicorn" app.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# 2. Start Frontend Vite Dev Server
echo "-> Starting Frontend Dashboard on http://localhost:5173..."
cd "$SCRIPT_DIR/frontend"
npm run dev -- --host 0.0.0.0 --port 5173 &
FRONTEND_PID=$!

echo ""
echo "Multi-Agent System is now live!"
echo "Backend API Docs: http://localhost:8000/docs"
echo "Dashboard UI:     http://localhost:5173"
echo "Press Ctrl+C to terminate both servers."

trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true; exit" SIGINT SIGTERM EXIT
wait
