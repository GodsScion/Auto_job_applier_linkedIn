@echo off
REM
REM Author:  Sai Vignesh Golla
REM License: MIT License  (https://opensource.org/license/mit)
REM GitHub:  https://github.com/GodsScion/Auto_job_applier_linkedIn
REM
REM Run the test suite on Windows. Double-click this file, or run it from a
REM terminal. It sets up the environment the first time, then runs the tests.

setlocal
cd /d "%~dp0"

set "PYLAUNCH="
py -3 --version >nul 2>&1 && set "PYLAUNCH=py -3"
if not defined PYLAUNCH (
    python --version >nul 2>&1 && set "PYLAUNCH=python"
)
if not defined PYLAUNCH (
    echo Python was not found. Install it from https://www.python.org/downloads/ and try again.
    pause
    exit /b 1
)

set "VENV_PY=.venv\Scripts\python.exe"
if not exist "%VENV_PY%" (
    echo Setting up the environment (first run)...
    %PYLAUNCH% -m venv .venv
)

"%VENV_PY%" -m pip install --quiet --upgrade pip
"%VENV_PY%" -m pip install --quiet -r requirements.txt -r requirements-dev.txt
if errorlevel 1 (
    echo Could not install dependencies.
    pause
    exit /b 1
)

"%VENV_PY%" -m pytest
echo.
pause
