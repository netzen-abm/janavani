# 🇮🇳 Janavani V2: Contributor & Collaborator Architecture Playbook

Thank you for contributing to Janavani V2. This platform is built to empower citizens to turn daily grievances into structured, lawful, and effective civic action through simple, privacy-first digital workflows.

---

## 🛡️ Our Core Structural Rules (Non-Negotiable)

Every line of code committed to this repository must respect our two foundational development constraints:

### 1. Privacy-by-Default (Zero-Persistent Ingestion Logs)
* **Rule:** The platform must never capture, log, write to disk, or index any identifiable user metrics (PII), geographic location coordinates, or plaintext citizen messages on remote hosting servers.
* **Implementation:** Downstream state caches are saved **in-memory only** inside volatile Redis pools with a strict **30-minute sliding window Time-To-Live (TTL)**. Persistent databases are forbidden in the ingestion pipeline.

### 2. Safety-by-Design (Strict Anti-Chat Enforcement)
* **Rule:** Janavani is an automated legal document formatting engine. It is **not** an open conversational chatbot or search assistant.
* **Implementation:** All inputs must pass through the `AirGappedKnowledgeGuardrail` script. Unstructured chatter or out-of-scope questions must be blocked instantly before they reach internal inference loops.

---

## 🛠️ Local Workspace Development Environment Setup

Follow this command sequence to install dependencies and configure your local multi-language toolchain (Python 3.11+ and Rust):

```bash
# 1. Clone the repository and navigate to the project directory
git clone https://github.com
cd janavani-website

# 2. Run the automated multi-language environment setup engine
chmod +x setup_dev.sh
./setup_dev.sh
```

### What `setup_dev.sh` configures automatically:
* Instantiates an isolated Python virtual environment (`venv/`) and maps required libraries (FastAPI, Celery, Pytest, ReportLab).
* Downloads the Rust WebAssembly toolchain target compilation target (`wasm32-unknown-unknown`).
* Installs the `Dioxus CLI` tool bundle used to compile your cross-platform interface application views.
* Activates local **Gitleaks Pre-Commit Hooks** within your `.git/` folder to intercept and block accidental credential commits *before* they leave your machine.

---

## 🧪 Operational Testing & Quality Verification

Before submitting any Pull Request (PR), you must verify that your changes pass the global test suites cleanly. Run this orchestrator command locally:

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

### The verification sequence executes:
1. Python backend validation checks (API endpoints security, Redis caching rules, and prompt constraints).
2. Headless Rust Dioxus WebAssembly component tests (Local browser encryption loops and hardware checking parameters).

---

## 📁 Repository Codebase Layout Schema

Familiarize yourself with our directory structure to ensure your contributions fit clean separation rules perfectly:

* `src/web/app.py` — The core backend API ingestion gateway that manages omnichannel data streams securely.
* `src/web/worker.py` — Background Celery workers that process voice-to-text transcriptions and document generation loops asynchronously.
* `src/web_dioxus/src/` — The dynamic Dioxus Rust client core that runs smoothly across Android, iOS, and Web browsers.
* `src/core/document_templates.py` — Read-only, statically compiled sample letters and official petition formats.
* `src/services/legal_knowledge_guard.py` — The air-gapped security guardrail that screens inputs and blocks conversational chatter.

---

## 📮 Branch Git Commit Formatting Guidelines

We enforce strict semantic commit message structures to keep our version history clean and organized. Please format your commit messages precisely using these prefixes:

* **`feat(module):`** Use when introducing a completely new feature or tool (e.g., `feat(maps): build local utm to wgs84 converter loop`).
* **`refactor(module):`** Use when reorganizing existing code arrays without changing outer behaviors (e.g., `refactor(web): mount template routers to app root`).
* **`test(module):`** Use when writing new unit tests or adding validation checks (e.g., `test(security): author checks for dynamic anchors`).
* **`ops(infra):`** Use when modifying deployment automation configs, shell scripts, or container definitions (e.g., `ops(deploy): build production provisioning script`).
