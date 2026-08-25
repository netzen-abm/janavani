#!/usr/bin/env bash
# Archived legacy multi-surface entrypoint.
# This implementation coupled the Telegram bot lifecycle to the web server.
set -e

export PORT="${PORT:-8080}"

if [ -f /app/requirements.txt ]; then
  echo "Installing Python dependencies from /app/requirements.txt..."
  pip install --no-cache-dir -r /app/requirements.txt || true
fi

python -m src.bot_telegram &
BOT_PID=$!

python -m src.web

kill "$BOT_PID" 2>/dev/null || true
wait "$BOT_PID" 2>/dev/null || true
