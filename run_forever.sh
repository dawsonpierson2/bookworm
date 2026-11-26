#!/usr/bin/env bash
set -e

cd "$HOME/book-recommender"

# Ensure SQLite database and NYT Best Sellers / sample books are initialized
python3 -c "import app; app.init_db()"

# Stop any prior Gunicorn or Flask instances for BookWorm
pkill -f "gunicorn.*app:app" 2>/dev/null || true
pkill -f "python3 app.py" 2>/dev/null || true

# Start Gunicorn detached from the current terminal
nohup gunicorn --bind 0.0.0.0:5000 --workers 2 --access-logfile gunicorn.log --error-logfile gunicorn.log app:app >/dev/null 2>&1 &
sleep 2

pgrep -af "gunicorn.*app:app" || {
    echo "Gunicorn failed to start. Check gunicorn.log:"
    cat gunicorn.log
    exit 1
}

echo "BookWorm is runni
ng persistently on port 5000 (logs: ~/book-recommender/gunicorn.log)"
