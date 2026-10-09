#!/usr/bin/env bash
# Prefer installed runtimes; use the Codex bundled tools on this Mac when needed.
DOODLE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
DOODLE_BUNDLE="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies"
if ! command -v node >/dev/null 2>&1 && [ -x "$DOODLE_BUNDLE/node/bin/node" ]; then
  export PATH="$DOODLE_BUNDLE/node/bin:$PATH"
fi
if ! command -v pnpm >/dev/null 2>&1 && [ -x "$DOODLE_BUNDLE/bin/fallback/pnpm" ]; then
  export PATH="$DOODLE_BUNDLE/bin/fallback:$PATH"
fi
if [ -x "$DOODLE_BUNDLE/python/bin/python3" ]; then
  DOODLE_PYTHON="$DOODLE_BUNDLE/python/bin/python3"
else
  DOODLE_PYTHON="$(command -v python3 || true)"
fi
export DOODLE_ROOT DOODLE_PYTHON
mkdir -p "$DOODLE_ROOT/work/tmp"
export TMPDIR="$DOODLE_ROOT/work/tmp"
