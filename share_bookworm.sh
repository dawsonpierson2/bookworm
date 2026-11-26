#!/usr/bin/env bash
set -e

cd "$HOME/book-recommender"

# Stop any previous BookWorm Flask instance
pkill -f "python3 app.py" 2>/dev/null || true

# Start Flask on port 5000 and write logs to flask.log
nohup python3 app.py > flask.log 2>&1 &
FLASK_PID=$!
sleep 2

if ! kill -0 "$FLASK_PID" 2>/dev/null; then
    echo "Flask failed to start. Check flask.log:"
    cat flask.log
    exit 1
fi

echo "BookWorm Flask running (PID $FLASK_PID) on http://127.0.0.1:5000"
echo "Logs: ~/book-recommender/flask.log"
echo "------------------------------------------------------------"

if command -v cloudflared >/dev/null 2>&1; then
    echo "Starting Cloudflare Tunnel (share the https:// URL below with your friends):"
    cloudflared tunnel --url http://127.0.0.1:5000
elif command -v ngrok >/dev/null 2>&1; then
    echo "Starting ngrok Tunnel (share the https:// URL below with your friends):"
    ngrok http 5000
else
    echo "No tunnel client installed yet."
    echo "Install cloudflared or ngrok in Kali Linux, or run:"
    echo "  cloudflared tunnel --url http://127.0.0.1:5000"
fi
