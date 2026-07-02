#!/usr/bin/env bash
# entrypoint.sh — Process manager for ether-ocr
# Launches API server (:8000) and MCP server (:9001) in background.
# If either process dies, the container exits so Docker can restart it.
set -euo pipefail

echo "==> Starting ether-ocr API server on :8000"
python3 -m ether_ocr_api.server &
API_PID=$!

echo "==> Starting ether-ocr MCP server on :9001"
python3 -m ether_ocr_mcp.server --transport http --port 9001 &
MCP_PID=$!

echo "==> Both services running (API:${API_PID} MCP:${MCP_PID})"

wait -n 2>/dev/null || true

echo "==> A service stopped. Shutting down..."
kill $API_PID $MCP_PID 2>/dev/null || true
wait 2>/dev/null || true
exit 1
