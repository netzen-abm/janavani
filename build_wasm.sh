#!/usr/bin/env bash

# ==============================================================================
# JANAVANI WEBOSM PRODUCTION COMPILATION PIPELINE
# Compiles, optimizes, and compresses the Dioxus Rust client code into static SPA assets.
# ==============================================================================

# Exit immediately if any command pipeline encounters an error state
set -e

PROJECT_DIR="src/web_dioxus"
DIST_DIR="${PROJECT_DIR}/dist"

echo "======================================================================"
echo "🇮🇳 INITIALIZING JANAVANI HIGH-EFFICIENCY WASM PRODUCTION BUILD"
echo "======================================================================"
echo "Timestamp (UTC): $(date -u +'%Y-%m-%dT%H:%M:%SZ')"

# Navigate safely to the Rust target workspace root boundary
cd "$PROJECT_DIR"

# Ensure necessary compilation tooling targets are present locally
if ! command -v dx &> /dev/null; then
    echo "📦 Installing missing Dioxus CLI compiler tools..."
    cargo install dioxus-cli --version 0.5.2
fi

if ! command -v wasm-opt &> /dev/null; then
    echo "⚠️ Warning: 'wasm-opt' tool not detected. Binary optimization sizes may vary slightly."
fi

echo -e "\n🔹 [1/3] Triggering Production Aggressive Opt-Level WASM Build..."
# DX build command automatically generates HTML hooks, CSS scaffolds, and JS loaders
dx build --release --platform web

echo -e "\n🔹 [2/3] Verification of Generated Production Distribution Artifacts..."
if [ -d "dist" ] && [ -f "dist/index.html" ]; then
    echo "✔ Build artifacts validated successfully inside output directory context."
else
    echo "❌ Compilation Error: Expected index.html allocation target missing."
    exit 1
fi

echo -e "\n🔹 [3/3] Preparing Freenet Deployment Assets Mapping Manifest..."
# Create a dedicated static descriptor file mapping assets for freenet contract binding routes
cat <<EOF > dist/freenet.manifest.json
{
  "application": "janavani-decentralized-hub",
  "build_timestamp": "$(date -u +'%Y-%m-%dT%H:%M:%SZ')",
  "entry_point": "index.html",
  "privacy_by_default": true,
  "safety_by_design": true
}
EOF

echo "======================================================================"
echo "🎉 JANAVANI PRODUCTION WASM BUNDLE COMPILED SUCCESSFULLY."
echo "Output Target: ${PROJECT_DIR}/dist/"
echo "Ready for distribution over HTTPS web-servers or freenet.org decentralized networks."
echo "======================================================================"
