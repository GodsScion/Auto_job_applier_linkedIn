#!/bin/bash
#
# Author:  Sai Vignesh Golla
# License: MIT License
#          https://opensource.org/license/mit
# GitHub:  https://github.com/GodsScion/Auto_job_applier_linkedIn
#
# One-click launcher for Linux. Run it with:  ./start.sh
# It sets up everything the first time, then opens the control panel in your web
# browser. Safe to run again any time.

# Move into the project folder (this script's own folder).
cd "$(dirname "$0")" || exit 1

echo ""
echo "========================================================"
echo "  Auto Job Applier - starting your control panel"
echo "========================================================"
echo ""

# 1) Make sure Python 3 is installed.
if ! command -v python3 >/dev/null 2>&1; then
    echo "Python 3 was not found on this computer."
    echo "Please install it (e.g. 'sudo apt install python3 python3-venv') and run this again."
    exit 1
fi

VENV_PY=".venv/bin/python"

# 2) Create a private Python environment the first time.
if [ ! -x "$VENV_PY" ]; then
    echo "Setting up for the first time (this can take a minute)..."
    python3 -m venv .venv || { echo "Could not create the Python environment. You may need the 'python3-venv' package."; exit 1; }
fi

# 3) Install the required packages once (quietly).
if [ ! -f ".venv/.deps_installed" ]; then
    echo "Installing required packages (one time only)..."
    "$VENV_PY" -m pip install --quiet --upgrade pip
    "$VENV_PY" -m pip install --quiet -r requirements.txt || { echo "Could not install required packages."; exit 1; }
    touch ".venv/.deps_installed"
fi

# 4) Start the control panel. It chooses a free port, prints the address, and
#    opens your browser to it.
export PANEL_OPEN_BROWSER=1

echo ""
echo "Starting the control panel and opening it in your browser..."
echo "The address is printed below. Keep this terminal open; press Ctrl+C to stop."
echo ""

# 5) Start the local control panel (runs until you press Ctrl+C).
"$VENV_PY" app.py
