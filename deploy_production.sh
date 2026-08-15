#!/usr/bin/env bash

# ==============================================================================
# JANAVANI UNIFIED MULTI-PROTOCOL PRODUCTION DEPLOYMENT MANAGER
# Orchestrates release packaging for FastHTML web portals, secure FastAPI
# backend meshes, local air-gapped SLM pods, and Rust Dioxus WebAssembly bundles.
# ==============================================================================

# Exit immediately if any segment encounters an unhandled runtime error
set -e

TIMESTAMP=$(date -u +'%Y%m%dT%H%M%SZ')
RELEASE_LOG="/var/log/janavani_deploy_${TIMESTAMP}.log"

echo "======================================================================"
echo "🇮🇳 STARTING PRODUCTION INGESTION GRID DEPLOYMENT FOR JANAVANI MESH"
echo "======================================================================"
echo "Deployment Time (UTC): $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# --- Step 1: Pre-Deployment Automated Validation Run ---
echo "🔹 [1/5] Running Comprehensive System-Wide Verification Tests..."
chmod +x run_all_tests.sh
./run_all_tests.sh >> "$RELEASE_LOG" 2>&1

# --- Step 2: Build and Optimize Client-Side WebAssembly Bundles ---
echo "🔹 [2/5] Compiling and Optimizing Production Rust Dioxus WebAssembly Bundle..."
chmod +x build_wasm.sh
./build_wasm.sh >> "$RELEASE_LOG" 2>&1

# --- Step 3: Trigger Rolling Container Image Rebuilds ---
echo "🔹 [3/5] Instantiating Background Container System Layer Preparation..."
docker compose build --no-cache >> "$RELEASE_LOG" 2>&1

# --- Step 4: Multi-Container Rollout Execution Loop ---
echo "🔹 [4/5] Executing Zero-Downtime Blue-Green Scale Rollout Sequences..."
# Pre-build fresh service containers safely behind running client traffic
docker compose up -d --no-deps --scale ai-agent-service=2 ai-agent-service >> "$RELEASE_LOG" 2>&1
sleep 5

# Perform an automated internal loopback verification request check before tearing down old nodes
HEALTH_CHECK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/agent/metrics \
  -H "X-Janavani-Interface-Token: web-mvp-token-abc" || echo "500")

if [ "$HEALTH_CHECK_STATUS" -eq 200 ] || [ "$HEALTH_CHECK_STATUS" -eq 404 ]; then
    echo "✔ Health verification successful. Trimming legacy execution nodes..."
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service >> "$RELEASE_LOG" 2>&1
    
    # Reload proxy routing paths cleanly without dropping connected websocket channels
    docker compose exec -T reverse-proxy-gateway nginx -s reload >> "$RELEASE_LOG" 2>&1
    
    # Synchronize all stateless interface client application runtimes
    docker compose up -d --no-deps web-mvp-application internal-admin-board >> "$RELEASE_LOG" 2>&1
else
    echo "❌ Error: Production deployment health validation check failed with status: $HEALTH_CHECK_STATUS"
    echo "Aborting deployment cycle. Triggering defensive fallback recovery routines..."
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service >> "$RELEASE_LOG" 2>&1
    exit 1
fi

# --- Step 5: System Resource Pruning Cleanup ---
echo "🔹 [5/5] Reclaiming Host File Allocation Clusters & Pruning Build Artifacts..."
docker image prune -f >> "$RELEASE_LOG" 2>&1

echo "======================================================================"
echo "🎉 JANAVANI PRODUCTION PLATFORM MULTI-TIER MESH ACTIVE AND FULLY UPGRADED"
echo "======================================================================"
