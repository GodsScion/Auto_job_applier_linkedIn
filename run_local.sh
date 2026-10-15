#!/usr/bin/env bash
# Set up and run the local control panel. This script does not start an application run.
set -euo pipefail

cd "$(dirname "$0")"

python_is_supported() {
    local candidate="$1"
    [ -x "$candidate" ] && "$candidate" -c 'import sys; raise SystemExit(0 if sys.version_info >= (3, 10) else 1)' >/dev/null 2>&1
}

find_python() {
    local candidate
    for candidate in python3.13 python3.12 python3.11 python3.10 python3; do
        if command -v "$candidate" >/dev/null 2>&1 && python_is_supported "$(command -v "$candidate")"; then
            command -v "$candidate"
            return 0
        fi
    done
    return 1
}

PYTHON=""
if python_is_supported ".venv/bin/python"; then
    VENV_DIR=".venv"
elif python_is_supported ".venv-python312/bin/python"; then
    VENV_DIR=".venv-python312"
else
    if ! PYTHON="$(find_python)"; then
        if command -v brew >/dev/null 2>&1; then
            echo "Python 3.10+ was not found. Installing Python 3.12 with Homebrew..."
            brew install python@3.12
            PYTHON="$(brew --prefix python@3.12)/bin/python3.12"
        else
            echo "Python 3.10+ was not found, and Homebrew is not installed."
            echo "Install Python 3.12 from https://www.python.org/downloads/ or install Homebrew and rerun this script."
            exit 1
        fi
    fi

    if [ -e ".venv" ]; then
        VENV_DIR=".venv-python312"
    else
        VENV_DIR=".venv"
    fi

    if ! python_is_supported "$VENV_DIR/bin/python"; then
        echo "Creating project environment with $PYTHON..."
        "$PYTHON" -m venv "$VENV_DIR"
    fi
fi

VENV_PY="$VENV_DIR/bin/python"
if ! python_is_supported "$VENV_PY"; then
    echo "The project environment is not using Python 3.10 or newer: $VENV_DIR"
    exit 1
fi

echo "Installing or updating project dependencies..."
"$VENV_PY" -m pip install -r requirements.txt

echo "Starting the local control panel. Keep this window open to use it."
PANEL_OPEN_BROWSER=1 "$VENV_PY" app.py
