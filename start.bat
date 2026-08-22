@echo off
REM
REM Author:  Sai Vignesh Golla
REM License: MIT License
REM          https://opensource.org/license/mit
REM GitHub:  https://github.com/GodsScion/Auto_job_applier_linkedIn
REM
REM One-click launcher for Windows. Double-click this file. It sets up everything
REM the first time, then opens the control panel in your web browser. Safe to run
REM again any time.

setlocal
cd /d "%~dp0"

echo.
echo ========================================================
echo   Auto Job Applier - starting your control panel
echo ========================================================
echo.

REM 1) Find Python (prefer the "py" launcher, fall back to "python").
set "PYLAUNCH="
py -3 --version >nul 2>&1 && set "PYLAUNCH=py -3"
if not defined PYLAUNCH (
    python --version >nul 2>&1 && set "PYLAUNCH=python"
)
if not defined PYLAUNCH (
    echo Python was not found on this computer.
    echo Please install it from https://www.python.org/downloads/ or the Microsoft Store,
    echo make sure "Add Python to PATH" is checked, then run this again.
    echo.
    pause
    exit /b 1
)

set "VENV_PY=.venv\Scripts\python.exe"

REM 2) Create a private Python environment the first time.
if not exist "%VENV_PY%" (
    echo Setting up for the first time (this can take a minute)...
    %PYLAUNCH% -m venv .venv
    if errorlevel 1 (
        echo Could not create the Python environment.
        pause
        exit /b 1
    )
)

REM 3) Install the required packages once (quietly).
if not exist ".venv\.deps_installed" (
    echo Installing required packages (one time only)...
    "%VENV_PY%" -m pip install --quiet --upgrade pip
    "%VENV_PY%" -m pip install --quiet -r requirements.txt
    if errorlevel 1 (
        echo Could not install required packages.
        pause
        exit /b 1
    )
    echo done> ".venv\.deps_installed"
)

REM 4) Start the control panel. It chooses a free port, prints the address, and
REM    opens your browser to it.
set "PANEL_OPEN_BROWSER=1"

echo.
echo Starting the control panel and opening it in your browser...
echo Keep this window open while you use the tool. Close it to stop the server.
echo.

REM 5) Start the local control panel (runs until you close this window).
"%VENV_PY%" app.py

echo.
echo The control panel has stopped.
pause
