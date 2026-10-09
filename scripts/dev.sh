#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/runtime.sh"
cd "$DOODLE_ROOT"
if [ ! -x backend/.venv/bin/python ] || [ ! -d frontend/node_modules ]; then
  echo 'Run bash scripts/setup.sh first.' >&2
  exit 1
fi
backend/.venv/bin/python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload --reload-dir backend/app --no-access-log &
DOODLE_BACKEND_PID=$!
(cd frontend && exec pnpm dev --host 127.0.0.1 --port 5173) &
DOODLE_FRONTEND_PID=$!
cleanup() { kill "$DOODLE_BACKEND_PID" "$DOODLE_FRONTEND_PID" 2>/dev/null || true; }
trap cleanup EXIT INT TERM
echo 'DoodleSteps: http://127.0.0.1:5173 — API: http://127.0.0.1:8000/docs'
wait
