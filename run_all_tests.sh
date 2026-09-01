#!/usr/bin/env bash

# JANAVANI — canonical validation orchestrator
#
# Rules:
# - Fail fast on test/build failure.
# - Never delete source or generated artifacts.
# - Use mock AI credentials for tests.
# - Keep Python and Rust validation separate.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-mock-verification-token}"
export HF_TOKEN="${HF_TOKEN:-mock-verification-token}"

printf '\n========================================\n'
printf 'JANAVANI CANONICAL VALIDATION SUITE\n'
printf '========================================\n'
printf 'Repository: %s\n\n' "$ROOT_DIR"

printf '%s\n' "[1/2] Running Python test suite..."
python -m pytest tests -v

if [[ -f "$ROOT_DIR/src/web_dioxus/Cargo.toml" ]]; then
    printf '%s\n' "[2/2] Running Rust/Dioxus tests..."
    (
        cd "$ROOT_DIR/src/web_dioxus"
        cargo test -- --nocapture
    )
else
    printf '%s\n' "[2/2] Rust/Dioxus package not present; skipping."
fi

printf '\n========================================\n'
printf 'JANAVANI VALIDATION SUITE PASSED\n'
printf '========================================\n'
