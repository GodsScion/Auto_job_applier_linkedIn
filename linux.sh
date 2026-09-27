#!/usr/bin/env bash

set -e

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_PY="$PROJECT/.venv/bin/python"

echo "======================================"
echo " Auto Job Applier - Linux Launcher"
echo "======================================"

# --------------------------------------------------
# 1. Check operating system
# --------------------------------------------------

if [ "$(uname -s)" != "Linux" ]; then
    echo "ERROR: This launcher currently supports Linux only."
    exit 1
fi

# --------------------------------------------------
# 2. Check/install system dependencies
# --------------------------------------------------

echo
echo "Checking Linux dependencies..."

MISSING=()

for cmd in python3 xdpyinfo xdotool wmctrl; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        MISSING+=("$cmd")
    fi
done

if [ "${#MISSING[@]}" -gt 0 ]; then
    echo "Some Linux dependencies are missing."
    echo "Installing required packages..."

    sudo apt update

    sudo apt install -y \
        python3 \
        python3-pip \
        python3-venv \
        x11-utils \
        x11-xserver-utils \
        xdotool \
        wmctrl \
        libx11-6 \
        libxext6 \
        libxrender1 \
        libxtst6
fi

# --------------------------------------------------
# 3. Detect Brave
# --------------------------------------------------

echo
echo "Checking browser..."

if command -v brave-browser >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v brave-browser)"
elif command -v brave >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v brave)"
else
    echo "ERROR: Brave browser was not found."
    echo "Please install Brave and run this script again."
    exit 1
fi

echo "BROWSER_BINARY=$BROWSER_BINARY"

# --------------------------------------------------
# 4. Configure GUI session
# --------------------------------------------------

export DISPLAY="${DISPLAY:-:0}"

if [ -z "${XAUTHORITY:-}" ] && [ -f "$HOME/.Xauthority" ]; then
    export XAUTHORITY="$HOME/.Xauthority"
fi

echo "DISPLAY=$DISPLAY"
echo "XAUTHORITY=${XAUTHORITY:-not set}"

# --------------------------------------------------
# 5. Verify X11
# --------------------------------------------------

echo
echo "Checking graphical environment..."

if ! xdpyinfo >/dev/null 2>&1; then
    echo
    echo "ERROR: Cannot connect to the X11 display."
    echo "DISPLAY=$DISPLAY"
    echo
    echo "Run this launcher from a terminal inside your graphical"
    echo "Linux desktop session."
    exit 1
fi

echo "X11 connection: OK"

# --------------------------------------------------
# 6. Create Python virtual environment
# --------------------------------------------------

echo
echo "Checking Python environment..."

if [ ! -x "$VENV_PY" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$PROJECT/.venv"
fi

# --------------------------------------------------
# 7. Install Python dependencies
# --------------------------------------------------

if [ ! -f "$PROJECT/.venv/.deps_installed" ] ||
   [ "$PROJECT/requirements.txt" -nt "$PROJECT/.venv/.deps_installed" ]; then

    echo
    echo "Installing Python dependencies..."

    "$VENV_PY" -m pip install --upgrade pip
    "$VENV_PY" -m pip install -r "$PROJECT/requirements.txt"

    touch "$PROJECT/.venv/.deps_installed"
fi

# --------------------------------------------------
# 8. Test PyAutoGUI
# --------------------------------------------------

echo
echo "Checking PyAutoGUI..."

"$VENV_PY" - <<'PY'
import pyautogui

print("PyAutoGUI: OK")
print("Screen size:", pyautogui.size())
PY

# --------------------------------------------------
# 9. Start application
# --------------------------------------------------

echo
echo "======================================"
echo " Starting automation bot"
echo "======================================"

cd "$PROJECT"

exec "$VENV_PY" ./start.sh