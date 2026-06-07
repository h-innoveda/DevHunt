#!/usr/bin/env bash
set -e

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

# Check venv
if [ ! -f "$BACKEND_DIR/venv/bin/python" ]; then
    echo "[ERROR] Virtual environment not found."
    echo "Run: cd backend && python3 -m venv venv && venv/bin/pip install -r requirements.txt"
    exit 1
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
