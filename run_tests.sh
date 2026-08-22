#!/bin/bash
#
# Author:  Sai Vignesh Golla
# License: MIT License  (https://opensource.org/license/mit)
# GitHub:  https://github.com/GodsScion/Auto_job_applier_linkedIn
#
# Run the test suite (Linux/macOS). Sets up the environment the first time,
# installs test dependencies, then runs pytest and prints a summary.
# Any extra arguments are passed through to pytest, e.g.:  ./run_tests.sh -k helpers

cd "$(dirname "$0")" || exit 1

VENV_PY=".venv/bin/python"
if [ ! -x "$VENV_PY" ]; then
    echo "Setting up the environment (first run)..."
    python3 -m venv .venv || { echo "Could not create the Python environment."; exit 1; }
fi

"$VENV_PY" -m pip install --quiet --upgrade pip
"$VENV_PY" -m pip install --quiet -r requirements.txt -r requirements-dev.txt \
    || { echo "Could not install dependencies."; exit 1; }

"$VENV_PY" -m pytest "$@"
