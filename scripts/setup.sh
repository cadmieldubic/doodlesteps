#!/usr/bin/env bash
set -euo pipefail
source "$(dirname "$0")/runtime.sh"
cd "$DOODLE_ROOT"
if [ -z "$DOODLE_PYTHON" ] || ! command -v node >/dev/null || ! command -v pnpm >/dev/null; then
  echo 'Install Python 3.12+, Node 22.12+, and pnpm 11.25+ before running setup.' >&2
  exit 1
fi
"$DOODLE_PYTHON" -m venv backend/.venv
export PIP_CACHE_DIR="$DOODLE_ROOT/work/pip-cache"
backend/.venv/bin/python -m pip install -r backend/requirements.lock
backend/.venv/bin/python -m pip install --no-deps -e 'backend[dev]'
(cd frontend && pnpm install --frozen-lockfile)
(cd frontend && PLAYWRIGHT_BROWSERS_PATH="$DOODLE_ROOT/work/playwright" pnpm exec playwright install chromium)
echo 'Ready. Run bash scripts/dev.sh. Demos need no API key.'
