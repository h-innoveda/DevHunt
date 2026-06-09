#!/usr/bin/env bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
URL="http://localhost:5000"

echo ""
echo "  ========================================"
echo "    DevHunt | AI Assistant Starting..."
echo "  ========================================"
echo "  Created by : Hitesh Solanki"
echo "  Website    : https://hiteshsolanki.in"
echo "  Email      : solankihiteshpankajbhai7@gmail.com"
echo "  Mobile     : +91 9327810431"
echo "  ----------------------------------------"
echo ""

# 1. Check Python version and installation
if ! command -v python3 &> /dev/null && ! command -v python &> /dev/null; then
    echo "[ERROR] Python is not installed. Please install Python 3 and try again."
    exit 1
fi

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then
    PYTHON_CMD="python"
fi

# 2. Check if virtual environment exists, if not create it
if [ ! -d "$BACKEND_DIR/venv" ]; then
    echo "[INFO] Creating Python virtual environment..."
    $PYTHON_CMD -m venv "$BACKEND_DIR/venv"
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment."
        exit 1
    fi
fi

# 3. Install required libraries
echo "[INFO] Installing required libraries from requirements.txt..."
if ! "$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"; then
    echo ""
    echo "[WARN] Dependency installation failed. This might be a pip version issue."
    read -p "May I update pip? (Y/N): " choice
    if [[ "$choice" =~ ^[Yy]$ ]]; then
        echo "[INFO] Updating pip..."
        "$BACKEND_DIR/venv/bin/python" -m pip install --upgrade pip
        echo "[INFO] Retrying dependency installation..."
        if ! "$BACKEND_DIR/venv/bin/pip" install -r "$BACKEND_DIR/requirements.txt"; then
            echo "[ERROR] Dependency installation failed again. Please check your internet connection or package compatibility."
            exit 1
        fi
    else
        echo "[WARN] Skipping pip update. Trying to run the code anyway..."
    fi
fi

cd "$BACKEND_DIR"

# Start Flask in background
echo "[1/3] Starting Flask server on $URL ..."
nohup venv/bin/python app.py > /tmp/devhunt.log 2>&1 &
SERVER_PID=$!
echo "      Server PID: $SERVER_PID"

# Wait for server
echo "[2/3] Waiting for server to start..."
sleep 3

# Check server is up
if ! curl -s --max-time 2 "$URL" > /dev/null; then
    echo "[WARN] Server may still be starting..."
fi

# Detect and open browser
echo "[3/3] Opening browser..."

open_browser() {
    local url="$1"
    # macOS
    if command -v open &>/dev/null; then
        open "$url"; return
    fi
    # Linux — try common browsers
    for browser in google-chrome chromium-browser chromium firefox xdg-open; do
        if command -v "$browser" &>/dev/null; then
            "$browser" "$url" &>/dev/null & return
        fi
    done
    echo "[INFO] Could not detect browser. Open manually: $url"
}

open_browser "$URL"

echo ""
echo "  Server running at: $URL"
echo "  Logs page:         $URL/logs"
echo "  Server log:        /tmp/devhunt.log"
echo "  To stop:           kill $SERVER_PID"
echo ""
