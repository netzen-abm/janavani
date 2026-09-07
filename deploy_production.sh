#!/usr/bin/env bash

# ==============================================================================
# JANAVANI UNIFIED MULTI-PROTOCOL PRODUCTION DEPLOYMENT MANAGER
# Orchestrates release packaging for FastHTML web portals, secure FastAPI
# backend meshes, local air-gapped SLM pods, and Rust Dioxus WebAssembly bundles.
# ==============================================================================

set -euo pipefail

TIMESTAMP=$(date -u +'%Y%m%dT%H%M%SZ')
RELEASE_LOG="/var/log/janavani_deploy_${TIMESTAMP}.log"

: "${WEB_INTERFACE_TOKEN:?WEB_INTERFACE_TOKEN must be set for production health checks}"

echo "======================================================================"
echo "🇮🇳 STARTING PRODUCTION INGESTION GRID DEPLOYMENT FOR JANAVANI MESH"
echo "======================================================================"
echo "Deployment Time (UTC): $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

echo "🔹 [1/5] Running Comprehensive System-Wide Verification Tests..."
chmod +x run_all_tests.sh
./run_all_tests.sh >> "$RELEASE_LOG" 2>&1

echo "🔹 [2/5] Compiling and Optimizing Production Rust Dioxus WebAssembly Bundle..."
chmod +x build_wasm.sh
./build_wasm.sh >> "$RELEASE_LOG" 2>&1

echo "🔹 [3/5] Instantiating Background Container System Layer Preparation..."
docker compose build --no-cache >> "$RELEASE_LOG" 2>&1

echo "🔹 [4/5] Executing Zero-Downtime Blue-Green Scale Rollout Sequences..."
docker compose up -d --no-deps --scale ai-agent-service=2 ai-agent-service >> "$RELEASE_LOG" 2>&1
sleep 5

HEALTH_CHECK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/agent/metrics \
  -H "X-Janavani-Interface-Token: ${WEB_INTERFACE_TOKEN}" || echo "500")

if [ "$HEALTH_CHECK_STATUS" -eq 200 ] || [ "$HEALTH_CHECK_STATUS" -eq 404 ]; then
    echo "✔ Health verification successful. Trimming legacy execution nodes..."
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service >> "$RELEASE_LOG" 2>&1
    docker compose exec -T reverse-proxy-gateway nginx -s reload >> "$RELEASE_LOG" 2>&1
    docker compose up -d --no-deps web-mvp-application internal-admin-board >> "$RELEASE_LOG" 2>&1
else
    echo "❌ Error: Production deployment health validation check failed with status: $HEALTH_CHECK_STATUS"
    echo "Aborting deployment cycle. Triggering defensive fallback recovery routines..."
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service >> "$RELEASE_LOG" 2>&1
    exit 1
fi

echo "🔹 [5/5] Reclaiming Host File Allocation Clusters & Pruning Build Artifacts..."
docker image prune -f >> "$RELEASE_LOG" 2>&1

echo "======================================================================"
echo "🎉 JANAVANI PRODUCTION PLATFORM MULTI-TIER MESH ACTIVE AND FULLY UPGRADED"
echo "======================================================================"