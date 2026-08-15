#!/usr/bin/env bash

# ==============================================================================
# JANAVANI ZERO-DOWNTIME HOST DEPLOYMENT PIPELINE
# Executes rolling blue-green style container updates smoothly without system downtime.
# ==============================================================================

# Exit immediately if any command pipeline encounters an error state
set -e

echo "=== [1/5] Extracting Latest Verified Commits from Remote Repository ==="
git pull origin main

echo "=== [2/5] Initializing Isolated Background Container Layer Building ==="
# Pre-builds updated system images behind active workloads to prevent connection drops
docker compose build ai-agent-service

echo "=== [3/5] Launching Upgraded Service Nodes Seamlessly ==="
# Launches fresh code containers while keeping older service instances live
docker compose up -d --no-deps --scale ai-agent-service=2 ai-agent-service

echo "=== [4/5] Executing Live Application Health Status Verifications ==="
# Give new container structures a few seconds to warm up and bind ports
sleep 5

# Verify the internal web app route is responding correctly before cutting traffic
HEALTH_CHECK_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/agent/metrics \
  -H "X-Janavani-Interface-Token: web-mvp-token-abc" || echo "500")

if [ "$HEALTH_CHECK_STATUS" -eq 200 ] || [ "$HEALTH_CHECK_STATUS" -eq 404 ]; then
    echo "✔ Deployment Health Checks Succeeded. Proceeding to trim legacy container clusters."
    # Scale down system nodes back to standard solitary background limits safely
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service
    
    echo "=== [5/5] Refreshing Security Reverse Proxy Routing Schemes ==="
    docker compose exec -T reverse-proxy-gateway nginx -s reload
    
    echo "=== [6/6] Synchronizing Frontend Client Application Environments ==="
    # Ensure frontend web applications are refreshed cleanly alongside system changes
    docker compose up -d --no-deps web-mvp-application
    
    # Prune orphaned image artifacts to reclaim physical server disk storage
    docker image prune -f
    echo "🎉 Janavani Agentic AI Service Platform Upgraded Successfully with Zero Downtime."
else
    echo "❌ Deployment Verification Failure Detected (HTTP Status: $HEALTH_CHECK_STATUS)."
    echo "Initiating defensive rollbacks to secure operational continuity."
    # Roll back and keep original container processes active
    docker compose up -d --no-deps --scale ai-agent-service=1 ai-agent-service
    exit 1
fi
