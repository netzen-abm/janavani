#!/usr/bin/env bash

# ==============================================================================
# JANAVANI V2 UNIFIED HOST DEPLOYMENT AND PROVISIONING SCRIPT
# Installs system dependencies, sets environment variables, and spins up services.
# ==============================================================================

set -e

echo "======================================================================"
echo "🇮🇳 INITIALIZING JANAVANI V2 MASTER MULTI-SERIVCE PRODUCTION WORKSPACE"
echo "======================================================================"

# Step 1: Install underlying system packages safely
echo "🔹 Step 1: Upgrading host core utility software repositories..."
sudo apt-get update && sudo apt-get install -y --no-install-recommends \
    curl git build-essential nginx redis-server python3-pip python3-venv \
    binaryen pkg-config libssl-dev

# Step 2: Assemble local project environments
echo "🔹 Step 2: Checking out active codebase tracks..."
if [ ! -d "janavani_v2" ]; then
    mkdir -p janavani_v2
fi

# Step 3: Trigger the unified system wide testing script shell engine
echo "🔹 Step 3: Triggering verification testing pipelines..."
chmod +x run_all_tests.sh
./run_all_tests.sh

# Step 4: Fire up Docker container layout groups
echo "🔹 Step 4: Launching isolated container sandbox structures..."
if command -v docker-compose &> /dev/null; then
    docker-compose up -d --build
else
    docker compose up -d --build
fi

echo "======================================================================"
echo "🎉 JANAVANI V2 PROVISIONING COMPLETED. MULTI-CHANNEL SERVICE MESH ONLINE"
echo "======================================================================"
