#!/usr/bin/env bash
# ==============================================================================
# CircuitRF M365 Copilot Agent Bridge Server (Linux / WSL Launcher)
# ==============================================================================

set -e
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR"

echo "[INFO] Starting CircuitRF Microsoft 365 Copilot Agent Bridge..."

if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "/home/satish/Documents/Code/dev/agent/venv/bin/activate" ]; then
    source /home/satish/Documents/Code/dev/agent/venv/bin/activate
fi

HOST="127.0.0.1"
PORT="8000"

echo "[INFO] CircuitRF MCP Bridge starting on http://${HOST}:${PORT}"
echo "[INFO] Interactive Swagger Documentation at http://${HOST}:${PORT}/docs"

exec python3 -m uvicorn bridge_server.server:app --host "$HOST" --port "$PORT" --reload
