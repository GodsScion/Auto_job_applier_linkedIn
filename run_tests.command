#!/bin/bash
#
# Author:  Sai Vignesh Golla
# License: MIT License  (https://opensource.org/license/mit)
# GitHub:  https://github.com/GodsScion/Auto_job_applier_linkedIn
#
# Run the test suite on macOS. Double-click this file in Finder (or run it from
# a terminal). It sets up the environment the first time, then runs the tests.

cd "$(dirname "$0")" || exit 1

VENV_PY=".venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "Setting up the environment (first run)..."
    python3 -m venv .venv || { echo "Could not create the Python environment."; read -r -p "Press Return to close..." _; exit 1; }
fi

"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet -r requirements.txt -r requirements-dev.txt \
    || { echo "Could not install dependencies."; read -r -p "Press Return to close..." _; exit 1; }

"$VENV_PY" -m pytest
echo ""
read -r -p "Tests finished. Press Return to close..." _
