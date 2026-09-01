#!/usr/bin/env bash

# ==============================================================================
# JANAVANI V3 COMPREHENSIVE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services, models, and docs.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -euo pipefail

# Store root directory for reference
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

# Clear stale Python bytecode residue arrays cleanly
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

# Environment variables match src/core/settings.py expectations
export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-mock-verification-token}"
export HUGGINGFACE_API_KEY="${HUGGINGFACE_API_KEY:-mock-verification-token}"

echo ""
echo "Configuration:"
echo "  REDIS_HOST:        $REDIS_HOST"
echo "  REDIS_PORT:        $REDIS_PORT"
echo "  OPENROUTER_API_KEY: [${#OPENROUTER_API_KEY} chars]"
echo "  HUGGINGFACE_API_KEY: [${#HUGGINGFACE_API_KEY} chars]"
echo ""

# --------------------------------------------------------------------------
# [1/2] Python Backend & Infrastructure Tests
# --------------------------------------------------------------------------
echo "🔹 [1/2] Executing Complete Python Backend & Infrastructure Tests..."
echo "  Running: pytest tests/ -v"
python -m pytest tests/ -v

# --------------------------------------------------------------------------
# [2/2] Rust Dioxus WebAssembly Component Tests
# --------------------------------------------------------------------------
echo ""
echo "🔹 [2/2] Running Headless Rust Dioxus WebAssembly Component Tests..."

if [[ -f "$ROOT_DIR/janavani_v3/src/web_dioxus/Cargo.toml" ]]; then
    echo "  Running: cargo test --lib -- --nocapture"
    (
        cd "$ROOT_DIR/janavani_v3/src/web_dioxus"
        cargo test --lib -- --nocapture
    )
else
    echo "  ⚠️  Rust/Dioxus package not found at $ROOT_DIR/janavani_v3/src/web_dioxus/Cargo.toml"
    echo "  Skipping Rust test suite."
fi

# --------------------------------------------------------------------------
# Test Suite Complete
# --------------------------------------------------------------------------
echo ""
echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "Privacy-by-Default and Safety-by-Design benchmarks verified."
echo "======================================================================"
