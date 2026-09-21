# 🇮🇳 Contributing to Janavani V3: Open-Source Ingestion Manual

Thank you for dedicating your time, technical skills, and legal expertise to Janavani. This platform is built to empower citizens to turn daily grievances into structured, lawful, and effective civic action through simple, privacy-first digital workflows.

---

## 🛡️ Our Core Operational Rules (Non-Negotiable)

Every contribution must align with our primary security architectures:

1. **Privacy-by-Default (Zero Server Tracking Logs):** We never capture, index, log, or store identifiable user data (PII), geographic location coordinates, or plaintext citizen messages on remote hosting servers. Data is processed in-memory and vanishes within 30 minutes.
2. **Safety-by-Design (Strict Anti-Chat Constraints):** The platform rejects conversational chatter or general search queries. Code modifications must keep the local AI engine strictly constrained to formatting official documentation sections.

---

## 💻 Local Workspace Development Environment Setup

Janavani uses a multi-language architecture built on Python 3.11+ and Rust. Run this command sequence to install system dependencies, pack requirements, and configure your local workspace toolchain:

```bash
# 1. Clone the codebase repository to your local system
git clone https://github.com
cd janavani-website

# 2. Execute the unified multi-language local installation script
chmod +x setup_dev.sh
./setup_dev.sh
```

### What `setup_dev.sh` configures automatically:
* Instantiates an isolated Python virtual environment (`venv/`) and maps required libraries (FastAPI, Celery, Pytest, ReportLab).
* Downloads the Rust WebAssembly target compilation architecture (`wasm32-unknown-unknown`).
* Installs the `Dioxus CLI` tool bundle used to compile your cross-platform interface application views.
* Activates local **Gitleaks Pre-Commit Hooks** within your `.git/` folder to intercept and block accidental credential commits *before* they leave your machine.

---

## 📮 Git Commit Message Formatting Guidelines

We use structured semantic prefixes to keep our version history clean and readable across multi-channel client teams. Please format your commit messages precisely using these guidelines:

* **`feat(module):`** Use when introducing a completely new feature or tool (e.g., `feat(maps): build local utm to wgs84 converter loop`).
* **`refactor(module):`** Use when reorganizing existing code arrays without changing outer behaviors (e.g., `refactor(web): mount template routers to app root`).
* **`test(module):`** Use when writing new unit tests or adding validation checks (e.g., `test(security): author checks for dynamic anchors`).
* **`ops(infra):`** Use when modifying deployment automation configs, shell scripts, or container definitions (e.g., `ops(deploy): build production provisioning script`).

---

## ⚖️ Constitutional Framework Alignment

When authoring document templates, automated letter formatting blocks, or escalation scripts, ensure your content anchors directly onto these supreme fundamental rights definitions:
* **The Preamble Foundation:** All petitions derive authority directly from the sovereign declaration **"WE, THE PEOPLE OF INDIA."**
* **The Golden Triangle Principles:** Content drafting must protect and highlight core protections under **Article 14 (Equality), Article 19 (Freedom), and Article 21 (Life and Dignity)**.
* **The Fundamental Duties Enforcer:** Connect civic monitoring loops to **Article 51A**, reminding public servants of their legal duties to protect public safety, infrastructure cleanliness, and administrative integrity.
