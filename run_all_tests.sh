#!/usr/bin/env bash

# ============================================================================
# JANAVANI — CANONICAL SYSTEM TEST ORCHESTRATOR
# ============================================================================
# Purpose:
#   Run the repository's Python domain/application tests and Rust validation
#   suites from one deterministic entry point.
# ============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-mock-verification-token}"
export HF_TOKEN="${HF_TOKEN:-mock-verification-token}"

printf '\n======================================================================\n'
printf 'JANAVANI CANONICAL VALIDATION SUITE\n'
printf '======================================================================\n'
printf 'Repository: %s\n\n' "$ROOT_DIR"

printf '%s\n' "[1/4] Running complete Python test suite..."
python -m pytest tests -v

printf '%s\n' "[2/4] Running canonical Rust domain-kernel tests..."
cargo test -p janavani-core -- --nocapture

printf '%s\n' "[3/4] Running canonical Rust application-boundary tests..."
cargo test -p janavani-application -- --nocapture

printf '%s\n' "[4/4] Running Rust/Dioxus package tests..."
if [[ -f "$ROOT_DIR/src/web_dioxus/Cargo.toml" ]]; then
    (
        cd "$ROOT_DIR/src/web_dioxus"
        cargo test -- --nocapture
    )
else
    printf '%s\n' "Rust/Dioxus package not present; skipping client suite."
fi

printf '\n======================================================================\n'
printf 'JANAVANI VALIDATION SUITE COMPLETED SUCCESSFULLY\n'
printf '======================================================================\n'
