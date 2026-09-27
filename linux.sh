#!/usr/bin/env bash

set -e

PROJECT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$PROJECT/.venv"
VENV_PY="$VENV/bin/python"

echo "======================================"
echo " Auto Job Applier - Linux Launcher"
echo "======================================"

# --------------------------------------------------
# 1. Check operating system
# --------------------------------------------------

if [ "$(uname -s)" != "Linux" ]; then
    echo
    echo "ERROR: This launcher currently supports Linux only."
    exit 1
fi

# --------------------------------------------------
# 2. Check/install system dependencies
# --------------------------------------------------

echo
echo "Checking Linux dependencies..."

MISSING=()

for cmd in python3 xdpyinfo xdotool wmctrl xhost; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        MISSING+=("$cmd")
    fi
done

if [ "${#MISSING[@]}" -gt 0 ]; then
    echo
    echo "Missing Linux dependencies:"
    printf '  - %s\n' "${MISSING[@]}"

    echo
    echo "Installing required packages..."

    if ! command -v sudo >/dev/null 2>&1; then
        echo
        echo "ERROR: sudo is required to install system dependencies."
        exit 1
    fi

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
# 3. Detect browser
# --------------------------------------------------

echo
echo "Checking browser..."

if command -v google-chrome >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v google-chrome)"

elif command -v google-chrome-stable >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v google-chrome-stable)"

elif command -v chromium >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v chromium)"

elif command -v chromium-browser >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v chromium-browser)"

elif command -v brave-browser >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v brave-browser)"

elif command -v brave >/dev/null 2>&1; then
    export BROWSER_BINARY="$(command -v brave)"

else
    echo
    echo "ERROR: No supported browser was found."
    echo
    echo "Supported browsers:"
    echo "  - Google Chrome"
    echo "  - Chromium"
    echo "  - Brave"
    exit 1
fi

echo "BROWSER_BINARY=$BROWSER_BINARY"

# --------------------------------------------------
# 4. Detect graphical session
# --------------------------------------------------

echo
echo "Checking graphical session..."

SESSION_TYPE="${XDG_SESSION_TYPE:-unknown}"

echo "XDG_SESSION_TYPE=$SESSION_TYPE"
echo "DISPLAY=${DISPLAY:-not set}"
echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-not set}"

if [ -z "${DISPLAY:-}" ]; then
    echo
    echo "ERROR: DISPLAY is not set."
    echo
    echo "This application requires an accessible X11/XWayland display."
    echo
    echo "Make sure you run this launcher from your graphical desktop"
    echo "terminal, not from a pure TTY."
    exit 1
fi

case "$SESSION_TYPE" in

    x11)
        echo
        echo "Native X11 session detected."
        ;;

    wayland)
        echo
        echo "Wayland session detected."
        echo "XWayland will be used for PyAutoGUI."
        ;;

    *)
        echo
        echo "WARNING: Unknown graphical session: $SESSION_TYPE"
        echo "Attempting to use the X display anyway."
        ;;

esac

# --------------------------------------------------
# 5. Configure X11/XWayland authentication
# --------------------------------------------------

echo
echo "Checking X11 authentication..."

if [ "$SESSION_TYPE" = "wayland" ]; then

    echo "Applying XWayland authorization for user: $USER"

    if ! xhost +SI:localuser:"$USER" >/dev/null 2>&1; then
        echo
        echo "ERROR: Could not configure XWayland authorization."
        echo
        echo "Current environment:"
        echo "  USER=$USER"
        echo "  DISPLAY=${DISPLAY:-not set}"
        echo "  XAUTHORITY=${XAUTHORITY:-not set}"
        echo "  XDG_SESSION_TYPE=$SESSION_TYPE"
        echo
        exit 1
    fi

    echo "XWayland authorization: OK"

else

    if [ -n "${XAUTHORITY:-}" ]; then
        echo "XAUTHORITY=$XAUTHORITY"

    elif [ -f "$HOME/.Xauthority" ]; then
        export XAUTHORITY="$HOME/.Xauthority"
        echo "XAUTHORITY=$XAUTHORITY"

    else
        echo "WARNING: XAUTHORITY is not set."
        echo "Continuing and letting X11 determine authentication."
    fi

fi

# --------------------------------------------------
# 6. Verify X11 / XWayland connection
# --------------------------------------------------

echo
echo "Checking graphical display..."

if ! xdpyinfo >/dev/null 2>&1; then
    echo
    echo "ERROR: Cannot connect to X11/XWayland display."
    echo
    echo "Current environment:"
    echo "  DISPLAY=${DISPLAY:-not set}"
    echo "  XAUTHORITY=${XAUTHORITY:-not set}"
    echo "  XDG_SESSION_TYPE=${SESSION_TYPE:-unknown}"
    echo "  WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-not set}"
    echo
    echo "Possible causes:"
    echo "  - XWayland is not running"
    echo "  - X11 authorization failed"
    echo "  - DISPLAY points to the wrong display"
    echo
    exit 1
fi

if [ "$SESSION_TYPE" = "wayland" ]; then
    echo "XWayland connection: OK"
else
    echo "X11 connection: OK"
fi

# --------------------------------------------------
# 7. Verify X11 tools
# --------------------------------------------------

echo
echo "Checking X11 automation tools..."

if ! xdotool getdisplaygeometry >/dev/null 2>&1; then
    echo
    echo "ERROR: xdotool cannot access the graphical display."
    echo
    exit 1
fi

echo "xdotool: OK"

if ! wmctrl -m >/dev/null 2>&1; then
    echo
    echo "ERROR: wmctrl cannot access the graphical display."
    echo
    exit 1
fi

echo "wmctrl: OK"

# --------------------------------------------------
# 8. Create Python virtual environment
# --------------------------------------------------

echo
echo "Checking Python environment..."

if [ ! -x "$VENV_PY" ]; then

    echo "Creating Python virtual environment..."

    python3 -m venv "$VENV"

    echo "Virtual environment created."

else

    echo "Virtual environment already exists."

fi

# --------------------------------------------------
# 9. Install Python dependencies
# --------------------------------------------------

if [ ! -f "$VENV/.deps_installed" ] || \
   [ "$PROJECT/requirements.txt" -nt "$VENV/.deps_installed" ]; then

    echo
    echo "Installing Python dependencies..."

    "$VENV_PY" -m pip install --upgrade pip

    "$VENV_PY" -m pip install -r "$PROJECT/requirements.txt"

    touch "$VENV/.deps_installed"

    echo
    echo "Python dependencies installed."

else

    echo
    echo "Python dependencies are already installed."

fi

# --------------------------------------------------
# 10. Verify PyAutoGUI
# --------------------------------------------------

echo
echo "Checking PyAutoGUI..."

if ! "$VENV_PY" - <<'PY'
import os
import pyautogui

print("PyAutoGUI import: OK")
print("DISPLAY:", os.environ.get("DISPLAY"))
print("XAUTHORITY:", os.environ.get("XAUTHORITY"))
print("XDG_SESSION_TYPE:", os.environ.get("XDG_SESSION_TYPE"))
print("Screen size:", pyautogui.size())
print("Mouse position:", pyautogui.position())
PY
then

    echo
    echo "ERROR: PyAutoGUI could not access the graphical display."
    echo
    echo "Environment:"
    echo "  DISPLAY=${DISPLAY:-not set}"
    echo "  XAUTHORITY=${XAUTHORITY:-not set}"
    echo "  XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-unknown}"
    echo "  WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-not set}"
    echo
    exit 1

fi

# --------------------------------------------------
# 11. Final environment information
# --------------------------------------------------

echo
echo "======================================"
echo " GUI environment ready"
echo "======================================"

echo "Session       : $SESSION_TYPE"
echo "Display       : ${DISPLAY:-not set}"
echo "XAuthority    : ${XAUTHORITY:-not set}"
echo "Browser       : $BROWSER_BINARY"
echo "Python        : $VENV_PY"

# --------------------------------------------------
# 12. Start application
# --------------------------------------------------

echo
echo "======================================"
echo " Starting automation bot"
echo "======================================"

cd "$PROJECT"

exec "$VENV_PY" "$PROJECT/runAiBot.py"