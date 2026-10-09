#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/runtime.sh"
cd "$DOODLE_ROOT"
export PLAYWRIGHT_BROWSERS_PATH="$DOODLE_ROOT/work/playwright"
backend/.venv/bin/python -m pytest backend/tests
backend/.venv/bin/python -m ruff check backend
backend/.venv/bin/python -m compileall -q backend/app
(cd frontend && pnpm test && pnpm typecheck && pnpm lint && pnpm build && pnpm test:e2e)
git diff --check
