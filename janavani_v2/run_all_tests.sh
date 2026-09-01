#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/2] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/2] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"
