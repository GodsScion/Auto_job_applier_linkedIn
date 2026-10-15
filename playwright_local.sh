#!/usr/bin/env bash
# Optional Playwright recorder/replayer for the local draft page only.
set -euo pipefail

cd "$(dirname "$0")"
PYTHON=".venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    PYTHON=".venv-python312/bin/python"
fi
if [ ! -x "$PYTHON" ]; then
    echo "Project Python environment not found. Run ./run_local.sh once first."
    exit 1
fi
if ! "$PYTHON" -c 'import playwright' >/dev/null 2>&1; then
    echo "Playwright is optional. Install it with:"
    echo "  $PYTHON -m pip install playwright"
    echo "  $PYTHON -m playwright install chromium"
    exit 1
fi

exec "$PYTHON" modules/playwright_local.py "$@"
