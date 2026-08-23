#!/usr/bin/env bash

# ============================================================================
# JANAVANI — CANONICAL SYSTEM TEST ORCHESTRATOR
# ============================================================================
# Purpose:
#   Run the repository's current Python and Rust/Dioxus validation suites from
#   one deterministic entry point.
#
# Rules:
#   - Fail fast on test/build failure.
#   - Do not delete source, database, or generated artifacts.
#   - Mock external AI credentials; never require production secrets for tests.
#   - Keep Python and Rust validation explicitly separated.
# ============================================================================

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT_DIR"

export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-mock-verification-token}"
export HUGGINGFACE_API_KEY="${HUGGINGFACE_API_KEY:-mock-verification-token}"

printf '\n======================================================================\n'
printf 'JANAVANI CANONICAL VALIDATION SUITE\n'
printf '======================================================================\n'
printf 'Repository: %s\n' "$ROOT_DIR"
printf '\n'

# --------------------------------------------------------------------------
# 1. Python test suite
# --------------------------------------------------------------------------
printf '%s\n' "[1/2] Running complete Python test suite..."
python -m pytest tests -v

# --------------------------------------------------------------------------
# 2. Rust/Dioxus package tests (only when the package is present)
# --------------------------------------------------------------------------
if [[ -f "$ROOT_DIR/src/web_dioxus/Cargo.toml" ]]; then
    printf '%s\n' "[2/2] Running Rust/Dioxus package tests..."
    (
        cd "$ROOT_DIR/src/web_dioxus"
        cargo test -- --nocapture
    )
else
    printf '%s\n' "[2/2] Rust/Dioxus package not present; skipping Rust suite."
fi

printf '\n======================================================================\n'
printf 'JANAVANI VALIDATION SUITE COMPLETED SUCCESSFULLY\n'
printf '======================================================================\n'
