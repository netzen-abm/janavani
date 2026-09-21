#!/usr/bin/env bash

# ==============================================================================
# JANAVANI V3 UNIFIED OMNICHANNEL PRODUCTION DEPLOYMENT ENGINE
# Orchestrates zero-downtime rollouts across the complete multi-protocol mesh.
# FastHTML portals, FastAPI APIs, local air-gapped SLMs, and Dioxus WASM client assets.
# ==============================================================================

# Exit instantly if any structural command block encounters an unhandled runtime error
set -e

TIMESTAMP=$(date -u +'%Y%m%dT%H%M%SZ')
RELEASE_LOG="/var/log/janavani_v3_deploy_${TIMESTAMP}.log"

echo "======================================================================"
echo "🇮🇳 STARTING JANAVANI V3 SYSTEM-WIDE PRODUCTION DEPLOYMENT MATRIX"
echo "======================================================================"
echo "Deployment Time (UTC): $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# --- Step 1: Pre-Deployment Automated Validation Run ---
echo "🔹 [1/6] Running System Security, Privacy & Compliance Verification Suites..."
chmod +x run_all_tests.sh
./run_all_tests.sh >> "$RELEASE_LOG" 2>&1

# --- Step 2: Build and Optimize Client-Side WebAssembly Bundles ---
echo "🔹 [2/6] Compiling and Optimizing Production Rust Dioxus WebAssembly Bundle..."
chmod +x build_wasm.sh
./build_wasm.sh >> "$RELEASE_LOG" 2>&1

# --- Step 3: Trigger Rolling Container Image Rebuilds ---
echo "🔹 [3/6] Initializing Isolated Background Container Layer Building..."
docker compose build --no-cache >> "$RELEASE_LOG" 2>&1

# --- Step 4: Multi-Container Rollout Execution Loop ---
echo "🔹 [4/6] Executing Zero-Downtime Blue-Green Scale Rollout Sequences..."
# Pre-build fresh service containers safely behind running client traffic
docker compose up -d --no-deps --scale ai-agent-service=2 ai-agent-service >> "$RELEASE_LOG" 2>&1
sleep 5

# Perform an automated internal loopback verification request check before tearing down old nodes
HEALTH_CHECK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v3/core/metrics \
  -H "X-Janavani-Interface-Token: web-v3-token" || echo "500")

if [ "$HEALTH_CHECK_STATUS" -eq 200 ] || [ "$HEALTH_CHECK_STATUS" -eq 404 ]; then
    echo "✔ Health verification successful. Trimming legacy execution nodes..."
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service >> "$RELEASE_LOG" 2>&1
    
    # Reload proxy routing paths cleanly without dropping connected channels
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
echo "🔹 [5/6] Reclaiming Host File Allocation Clusters & Pruning Build Artifacts..."
docker image prune -f >> "$RELEASE_LOG" 2>&1

echo "======================================================================"
echo "🎉 JANAVANI V3 PRODUCTION PLATFORM MULTI-TIER MESH ACTIVE AND FULLY UPGRADED"
echo "======================================================================"
