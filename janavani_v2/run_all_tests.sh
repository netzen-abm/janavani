#!/usr/bin/env bash
set -euo pipefail

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

# Store current directory to return after tests
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

echo "🔹 [1/2] Running Core Python System Component Tests..."
python -m pytest tests/ -v

echo ""
echo "🔹 [2/2] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
if [[ -f "$SCRIPT_DIR/src/web_dioxus/Cargo.toml" ]]; then
    (
        cd "$SCRIPT_DIR/src/web_dioxus"
        cargo test --lib -- --nocapture
    )
else
    echo "  ⚠️  Rust/Dioxus package not found. Skipping Rust test suite."
fi

echo ""
echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"
