#!/usr/bin/env bash

# ==============================================================================
# JANAVANI SYSTEM-WIDE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services and models.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/9] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/9] Running Geodetic Projections & KML Composer Subsystem Tests..."
pytest tests/test_geodetic_mapping.py -v

echo -e "\n🔹 [3/9] Checking Deployment Building Script Infrastructure Rules..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v

echo -e "\n🔹 [4/9] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# -------------------------

#!/usr/bin/env bash

# ==============================================================================
# JANAVANI SYSTEM-WIDE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services and models.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/8] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/8] Checking Deployment Building Script Infrastructure Rules..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v

echo -e "\n🔹 [3/8] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# ----------------------------------------------

#!/usr/bin/env bash

# ==============================================================================
# JANAVANI SYSTEM-WIDE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services and models.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/7] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/7] Checking Deployment Building Script Infrastructure Rules..."
pytest tests/test_build_pipeline.py -v

echo -e "\n🔹 [3/7] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# ---------------------------

#!/usr/bin/env bash

# ==============================================================================
# JANAVANI SYSTEM-WIDE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services and models.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -e

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/6] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/6] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
# Executes native cargo test sweeps inside your compiled frontend project directories
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# ------------------------

#!/usr/bin/env bash

# ==============================================================================
# JANAVANI SYSTEM-WIDE TEST ORCHESTRATOR
# Runs complete validation suites across all decoupled services and models.
# ==============================================================================

# Exit instantly if any structural component test encounters an uncaught failure
set -e

# Clear stale bytecode residues to enforce pristine cache generation
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"
echo "Timestamp (UTC): $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# Enforce secure virtual environment configuration anchors
export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

echo -e "\n🔹 [1/5] Running Core System Component Tests..."
pytest tests/test_ai_agent_components.py -v

echo -e "\n🔹 [2/5] Running Translation Layer & Mock Verification Tests..."
pytest tests/test_iit_madras_mock.py -v

echo -e "\n🔹 [3/5] Running Accountability Feedback Loop Verification Tests..."
pytest tests/test_accountability_feedback.py -v

echo -e "\n🔹 [4/5] Running Constitutional Enforcement & Document Pipeline Tests..."
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v

echo -e "\n🔹 [5/5] Performing Regional Vernacular Translation Code Verifications..."
pytest tests/test_vernacular_headers.py -v

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "Privacy-by-Default and Safety-by-Design benchmarks verified."
echo "======================================================================"
