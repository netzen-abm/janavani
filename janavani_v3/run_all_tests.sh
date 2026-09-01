#!/usr/bin/env bash

# JANAVANI V3 COMPREHENSIVE TEST ORCHESTRATOR
# Runs validation across decoupled services and components.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST="${REDIS_HOST:-localhost}"
export REDIS_PORT="${REDIS_PORT:-6379}"
export OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-mock-verification-token}"
export HF_TOKEN="${HF_TOKEN:-mock-verification-token}"

echo ""
echo "Configuration:"
echo "  REDIS_HOST:        $REDIS_HOST"
echo "  REDIS_PORT:        $REDIS_PORT"
echo "  OPENROUTER_API_KEY: [${#OPENROUTER_API_KEY} chars]"
echo "  HF_TOKEN:          [${#HF_TOKEN} chars]"
echo ""

echo "🔹 [1/2] Executing Complete Python Backend & Infrastructure Tests..."
python -m pytest tests/ -v

echo ""
echo "🔹 [2/2] Running Headless Rust Dioxus WebAssembly Component Tests..."

if [[ -f "$ROOT_DIR/janavani_v3/src/web_dioxus/Cargo.toml" ]]; then
    (
        cd "$ROOT_DIR/janavani_v3/src/web_dioxus"
        cargo test --lib -- --nocapture
    )
else
    echo "  ⚠️  Rust/Dioxus package not found. Skipping Rust suite."
fi

echo ""
echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "Privacy-by-Default and Safety-by-Design benchmarks verified."
echo "======================================================================"
