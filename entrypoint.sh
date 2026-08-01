#!/usr/bin/env bash
# entrypoint.sh - start bot in background, then run web health server in foreground
set -e

# Default PORT
export PORT="${PORT:-8080}"

# Ensure Python deps are installed at container start (helps if build step was skipped or cached)
if [ -f /app/requirements.txt ]; then
  echo "Installing Python dependencies from /app/requirements.txt..."
  pip install --no-cache-dir -r /app/requirements.txt || true
fi

# Start the telegram bot in background
python -m src.bot_telegram &
BOT_PID=$!

# Run the simple Flask health server in foreground
python -m src.web

# If web server exits for any reason, kill the bot and exit
kill "$BOT_PID" 2>/dev/null || true
wait "$BOT_PID" 2>/dev/null || true
