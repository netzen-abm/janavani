#!/usr/bin/env bash
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/15] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v
pytest tests/test_local_slm_prompts.py -v
pytest tests/test_geodetic_mapping.py -v
pytest tests/test_browser_capture_infra.py -v
pytest tests/test_emergency_lockdown.py -v
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v
pytest tests/test_production_integrity.py -v

echo -e "\n🔹 [2/15] Verifying Multi-Modal Ingestion & Community Network Registries..."
pytest tests/test_omnichannel_multimodal.py -v

echo -e "\n🔹 [3/15] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
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

echo -e "\n🔹 [1/16] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/16] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
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

echo -e "\n🔹 [1/16] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/16] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
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

echo -e "\n🔹 [1/17] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/17] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
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

echo -e "\n🔹 [1/18] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/18] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
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

echo -e "\n🔹 Running Complete Hardened Ingestion Test Suite..."
pytest tests/ -v

echo -e "\n🔹 Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
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

echo -e "\n🔹 [1/19] Running Core Python System Component Tests..."
pytest tests/ -v

echo -e "\n🔹 [2/18] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"




