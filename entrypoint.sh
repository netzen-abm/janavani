#!/usr/bin/env bash
# Janavani canonical web/API container entrypoint.
# Each ecosystem surface owns its own runtime; this process does not start
# Telegram, WhatsApp, Messenger, or any other client as a child process.
set -euo pipefail

export PORT="${PORT:-8080}"

exec uvicorn src.web.canonical_app:app --host 0.0.0.0 --port "${PORT}"
