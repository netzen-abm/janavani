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
