#!/usr/bin/env bash
set -e

# Clear bytecode residue arrays cleanly
find . -type d -name "__pycache__" -exec rm -r {} + 2>/dev/null || true

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI SECURITY, PRIVACY & COMPLIANCE VALIDATION SUITE"
echo "======================================================================"

export REDIS_HOST=localhost
export REDIS_PORT=6379
export OPENROUTER_API_KEY=mock-verification-token
export HUGGINGFACE_API_KEY=mock-verification-token

# Append your newly deployed security anchor module validation scripts right into the test loop
pytest tests/ -v

cd src/web_dioxus && cargo test --lib -- --nocapture


# -----------------------

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

echo -e "\n🔹 [1/14] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/14] Verifying Local Air-Gapped SLM Prompt Guardrails..."
pytest tests/test_local_slm_prompts.py -v

echo -e "\n🔹 [3/14] Running Geodetic Projections & KML Composer Subsystem Tests..."
pytest tests/test_geodetic_mapping.py -v

echo -e "\n🔹 [4/14] Verifying Browser Context Coordinate Injection Tool Scripts..."
pytest tests/test_browser_capture_infra.py -v

echo -e "\n🔹 [5/14] Validating Secure Emergency SOS Lockdown Routines..."
pytest tests/test_emergency_lockdown.py -v

echo -e "\n🔹 [6/14] Auditing Production Environment Configuration Security Standards..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v
pytest tests/test_production_integrity.py -v

echo -e "\n🔹 [7/14] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"



# --------------------------------

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

echo -e "\n🔹 [1/13] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/13] Running Geodetic Projections & KML Composer Subsystem Tests..."
pytest tests/test_geodetic_mapping.py -v

echo -e "\n🔹 [3/13] Verifying Browser Context Coordinate Injection Tool Scripts..."
pytest tests/test_browser_capture_infra.py -v

echo -e "\n🔹 [4/13] Validating Secure Emergency SOS Lockdown Routines..."
pytest tests/test_emergency_lockdown.py -v

echo -e "\n🔹 [5/13] Auditing Production Environment Configuration Security Standards..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v
pytest tests/test_production_integrity.py -v

echo -e "\n🔹 [6/13] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# --------------------------

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

echo -e "\n🔹 [1/12] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/12] Running Geodetic Projections & KML Composer Subsystem Tests..."
pytest tests/test_geodetic_mapping.py -v

echo -e "\n🔹 [3/12] Verifying Browser Context Coordinate Injection Tool Scripts..."
pytest tests/test_browser_capture_infra.py -v

echo -e "\n🔹 [4/12] Validating Secure Emergency SOS Lockdown Routines..."
pytest tests/test_emergency_lockdown.py -v

echo -e "\n🔹 [5/12] Checking Deployment Building Script Infrastructure Rules..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v

echo -e "\n🔹 [6/12] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


#

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

echo -e "\n🔹 [1/11] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/11] Running Geodetic Projections & KML Composer Subsystem Tests..."
pytest tests/test_geodetic_mapping.py -v

echo -e "\n🔹 [3/11] Verifying Browser Context Coordinate Injection Tool Scripts..."
pytest tests/test_browser_capture_infra.py -v

echo -e "\n🔹 [4/11] Validating Secure Emergency SOS Lockdown Routines..."
pytest tests/test_emergency_lockdown.py -v

echo -e "\n🔹 [5/11] Checking Deployment Building Script Infrastructure Rules..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v

echo -e "\n🔹 [6/11] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# ----------------------

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

echo -e "\n🔹 [1/10] Running Core Python System Component Tests..."
pytest tests/test_ai_agent_components.py -v
pytest tests/test_iit_madras_mock.py -v
pytest tests/test_accountability_feedback.py -v
pytest tests/test_constitutional_compliance.py -v
pytest tests/test_document_generation.py -v
pytest tests/test_vernacular_headers.py -v

echo -e "\n🔹 [2/10] Running Geodetic Projections & KML Composer Subsystem Tests..."
pytest tests/test_geodetic_mapping.py -v

echo -e "\n🔹 [3/10] Verifying Browser Context Coordinate Injection Tool Scripts..."
pytest tests/test_browser_capture_infra.py -v

echo -e "\n🔹 [4/10] Checking Deployment Building Script Infrastructure Rules..."
pytest tests/test_build_pipeline.py -v
pytest tests/test_setup_infrastructure.py -v

echo -e "\n🔹 [5/10] Running Headless Rust Dioxus WebAssembly Engine Component Tests..."
cd src/web_dioxus && cargo test --lib -- --nocapture

echo "======================================================================"
echo "🎉 ALL JANAVANI COMPONENT TEST CYCLES CONCLUDED SUCCESSFULLY."
echo "======================================================================"


# ----------------------

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
