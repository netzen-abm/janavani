#!/usr/bin/env bash

# ==============================================================================
# JANAVANI V3 COMPREHENSIVE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services, models, and docs.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -e

# Clear stale Python bytecode residue arrays cleanly
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/2] Executing Complete Python Backend & Infrastructure Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/2] Running Headless Rust Dioxus WebAssembly Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "Privacy-by-Default and Safety-by-Design benchmarks verified."
echo "======================================================================"

#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/20] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/20] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"

