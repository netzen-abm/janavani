#!/usr/bin/env bash

# ============================================================================
# JANAVANI — CANONICAL SYSTEM TEST ORCHESTRATOR
# ============================================================================
# Purpose:
#   Run the repository's Python domain/application tests and Rust validation
#   suites from one deterministic entry point.
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
export HF_TOKEN="${HF_TOKEN:-mock-verification-token}"

printf '\n======================================================================\n'
printf 'JANAVANI CANONICAL VALIDATION SUITE\n'
printf '======================================================================\n'
printf 'Repository: %s\n' "$ROOT_DIR"
printf '\n'

# --------------------------------------------------------------------------
# 1. Python test suite
# --------------------------------------------------------------------------
printf '%s\n' "[1/3] Running complete Python test suite..."
python -m pytest tests -v

# --------------------------------------------------------------------------
# 2. Canonical Rust domain kernel
# --------------------------------------------------------------------------
printf '%s\n' "[2/3] Running canonical Rust domain-kernel tests..."
cargo test --manifest-path "$ROOT_DIR/crates/janavani-core/Cargo.toml" -- --nocapture

# --------------------------------------------------------------------------
# 3. Rust/Dioxus client package (only when the package is present)
# --------------------------------------------------------------------------
printf '%s\n' "[3/3] Running Rust/Dioxus package tests..."
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
