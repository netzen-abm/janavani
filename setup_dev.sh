#!/usr/bin/env bash

# ==============================================================================
# JANAVANI UNIFIED MULTI-LANGUAGE LOCAL DEVELOPMENT INITIALIZATION ENGINE
# Configures Python 3.11+ and Rust compilation environments automatically.
# Sets up pre-commit hooks, system dependencies, and verification suites.
# ==============================================================================

# Exit instantly if any initialization configuration encounters an uncaught failure
set -e

echo "======================================================================"
echo "🇮🇳 INITIALIZING JANAVANI MULTI-PROTOCOL DEV INSTALATION ENVIRONMENT"
echo "======================================================================"
echo "Timestamp (UTC): $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# --- Step 1: System Package Engine Diagnostics ---
echo -e "\n🔹 [1/6] Verifying Toolchain Dependency Pre-requisites..."
for cmd in git python3 pip rustc cargo docker; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Error: Required toolchain component '$cmd' is not installed."
        echo "Please install this package dependency on your host layer before proceeding."
        exit 1
    fi
    echo "✔ Found component: $cmd"
done

# --- Step 2: Python Virtual Environment Matrix Setup ---
echo -e "\n🔹 [2/6] Assembling Isolated Python Virtual Workspace..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✔ Virtual environment layer instantiated."
fi
source venv/bin/activate

echo "📦 Upgrading pip packages and installing foundational library pools..."
pip install --upgrade pip
pip install -r src/web_mvp/requirements.txt
pip install pytest fakeredis pydantic pydantic-settings requests redis pre-commit httpx

# --- Step 3: WebAssembly Toolchain Compilation Profiles ---
echo -e "\n🔹 [3/6] Setting Up Rust WebAssembly Compilation Frameworks..."
cd src/web_dioxus
rustup target add wasm32-unknown-unknown

if ! command -v dx &> /dev/null; then
    echo "📦 Compiling and locking localized Dioxus CLI system tools..."
    cargo install dioxus-cli --version 0.5.2
fi
cd ../..

# --- Step 4: Defensive Pre-Commit Interception Installation ---
echo -e "\n🔹 [4/6] Activating Local Security Pre-Commit Protection Barriers..."
if [ -f ".pre-commit-config.yaml" ]; then
    pre-commit install
    echo "✔ Local client-side credential scanning hooks activated inside .git infrastructure."
else
    echo "⚠️ Warning: .pre-commit-config.yaml missing. Skipping hook setup blocks."
fi

# --- Step 5: Environment Profile Replication ---
echo -e "\n🔹 [5/6] Synchronizing Local Configuration Parameters Template..."
if [ -f ".env.example" ] && [ ! -f ".env" ]; then
    cp .env.example .env
    echo "✔ Copied environmental variable parameters baseline to local '.env' file layer."
else
    echo "✔ Active configuration layer token mapping file '.env' already present."
fi

# --- Step 6: End-to-End System-Wide Integration Validation ---
echo -e "\n🔹 [6/6] Executing Complete Verification Test Suites..."
chmod +x run_all_tests.sh
./run_all_tests.sh

echo -e "\n======================================================================"
echo "🎉 JANAVANI COMPOSITE DEVELOPMENT ENVIRONMENT INSTALLED SUCCESSFULLY."
echo "======================================================================"
echo "To begin local operations, run the following commands:"
echo "  1. source venv/bin/activate             <- Active your isolated workspace"
echo "  2. docker compose up -d                  <- Fire up your background caching grid"
echo "  3. ./build_wasm.sh                      <- Build your sovereign Dioxus client"
echo "======================================================================"
