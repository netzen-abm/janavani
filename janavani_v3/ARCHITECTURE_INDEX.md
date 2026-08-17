# 🇮🇳 Janavani V3: Master Platform Architecture Blueprint Index
**Version:** 3.0.0  
**Security Status:** STRICT ZERO-KNOWLEDGE / NO DATA RETENTION BY DEFAULT  
**Target Environments:** WebAssembly (WASM), Native Android (APK), Native iOS, Linux Sandbox Containers

This index maps every module, security firewall layer, background task worker, and cross-platform compilation anchor within Janavani V3's decentralized citizen-governance operating system.

---

## 📁 1. Root Repository Layout & System Configuration

### 🐳 `docker-compose.yml`
* **Role:** Multi-service container mesh topology coordinator.
* **Core Blueprints:**
  * Defines the internal bridge network sandbox (`janavani-secure-mesh`).
  * Deploys the isolated `local-slm-sandbox` (Ollama) container running local, air-gapped `Llama-3-8B-Instruct-4bit` models.
  * Deploys the non-persistent, in-memory **Volatile Redis Cache Grid** with disk-writing explicitly deactivated (`--appendonly no --save ""`).
* **Security Rule:** Prevents any plaintext citizen grievance input text, voice notes, or unique tracking indicators from ever hitting physical storage arrays.

### 🛡️ `nginx.conf`
* **Role:** Public-facing security reverse-proxy gateway and traffic firewall.
* **Core Blueprints:**
  * Enforces strict **TLS 1.3 mTLS encryption handshakes** on public Port 443.
  * Allocates split rate-limiting zones: `api_limit_zone` (max 10 requests/sec per client IP) and `sos_limit_zone` (hard capped at max 2 requests/min per IP).
  * Limits file uploads strictly to a maximum payload size of 2MB to block buffer overflow or resource exhaustion attacks.

### 🚀 `deploy_production.sh`
* **Role:** Automated zero-downtime Blue-Green rolling deployment pipeline manager.
* **Core Blueprints:**
  * Executes global multi-language test hooks (`run_all_tests.sh`) before updating containers.
  * Scales identical temporary backend tasks behind running proxy configurations to allow code upgrades with **zero connection drops**.
  * Performs automatic loopback curl network health verifications and triggers immediate rollback routines if endpoints respond with error status flags.

### 🧪 `run_all_tests.sh`
* **Role:** Multi-language continuous integration test execution orchestrator.
* **Core Blueprints:**
  * Automatically purges stale runtime `__pycache__` bytes across repositories to ensure a pristine testing environment.
  * Runs concurrent test sets spanning Python API gateways (`pytest`) and headless Rust WebAssembly engine files (`cargo test`).

---

## 📁 2. `src/web/` — Stateless Ingestion API Core & Background Task Workers

### 🧬 `app.py`
* **Role:** Stateless multi-modal API ingestion root gateway.
* **Core Blueprints:**
  * Ingests multipart form parameters (text, audio, images, videos) from multi-channel webhook nodes (Telegram, WhatsApp, Web MVP).
  * Mounts the **Anti-Chat Knowledge Guardrail** checks to block out-of-scope conversational inputs.
  * Verifies single-use, cryptographically signed rating tokens to prevent review manipulation on public office metrics pages.

### ⚙️ `worker.py`
* **Role:** Asynchronous background worker queue core (Celery + Redis).
* **Core Blueprints:**
  * Pulls media files asynchronously from the volatile broker grid to prevent interface timeout freezes.
  * Houses the AI4Bharat automated speech recognition (ASR) transcription algorithms to decode voice notes locally.
  * Automatically compiles finished legal paperwork outputs directly into binary arrays, returning them to volatile transient caches with a strict **30-minute sliding window expiration**.

### 🏛️ `land_router.py`
* **Role:** Stateless property tracking and ancestral land revenue ledger lookup proxy.
* **Core Blueprints:**
  * Ingests encrypted cadastral parameters (District, Tehsil, Village, Gata numbers).
  * Queries local read-only mock data pools or air-gapped registry nodes without saving tracking footprints on server drives.
  * Outputs the clean coordinate vertex arrays required for local client-side KML canvas maps rendering.

### 🎭 `de_linked_ingestion.py`
* **Role:** Multi-modal data shredder and arrival timeline scrambler.
* **Core Blueprints:**
  * Automatically shreds incoming multipart bundles into independent, de-linked data frames.
  * Processes image buffers locally through a binary filter to strip out all EXIF, GPS camera tags, and metadata tracking indices.
  * Applies a random time delay jitter (3.0 to 15.0 seconds) to mix up asset arrival lines, blocking side-channel traffic correlation attacks.

### 📊 `metrics_collector.py`
* **Role:** OpenMetrics-compliant server resource and telemetry extraction engine.
* **Core Blueprints:**
  * Computes active metrics covering host CPU loads, RAM memory pools, and the number of active temporary records in Redis.
  * Exposes formatted, abstract plain-text OpenMetrics lines to internal Prometheus scrapers.
  * Enforces a zero-user-context rule: **contains absolutely no citizen strings or identifier metrics**.

---

## 📁 3. `src/web_dioxus/src/` — Isomorphic Sovereign Rust Frontend SPA

### 🌟 `main.rs`
* **Role:** App layout coordinator, concurrent state tracker, and user dashboard.
* **Core Blueprints:**
  * Manages global cross-platform frontend loops for Android, iOS, and WebAssembly.
  * Utilizes Rust reactive primitives (`use_signal`) to handle dynamic configuration changes instantly without screen reloads.
  * Maps high-priority, universal panic action triggers directly onto screen widget grids.

### 🔌 `auto_transport.rs`
* **Role:** Invisible network middleware sensing core (The Connection Router).
* **Core Blueprints:**
  * Implements the **Invisible Middleware Rule**: continuously checks local system pings behind the scenes without user interaction.
  * Automatically switches routes: triggers the Nym Mixnet proxy mask if available, defaults to HTTPS with random delay jitter, or falls back directly to UHF/VHF radio frequencies over the **Reticulum Mesh Network** when offline.

### ⚡ `capability.rs`
* **Role:** Device hardware performance profiling inspector.
* **Core Blueprints:**
  * Queries browser concurrency levels and hardware memory pools via WebAssembly (`web-sys` navigator API).
  * Dynamically switches processing: forces powerful hardware to run the text compiler locally in WASM, but shifts low-tier budget mobile browsers onto server-assisted container workflows to prevent device freezes.

### 🛡️ `legal_shield.rs`
* **Role:** Three-part legal shield asynchronous escalation stack compiler.
* **Core Blueprints:**
  * Anchors all document generation headings directly to the supreme Preamble definition: **"WE, THE PEOPLE OF INDIA."**
  * Compiles an automated sequence of three documents to counter bureaucratic stalling:
    1. A primary **Grievance Representation** invoking Articles 14, 19, and 21.
    2. A calendar-locked, automated **RTI Form (Section 6(1))** to trace processing files.
    3. A formal **Disciplinary Escalation Memorandum** addressed to the state Chief Secretary, invoking the Bharatiya Sakshya Adhiniyam 2023 (Sections 74 & 75).

### 🥷 `privacy_audit.rs`
* **Role:** Zero-collection client-side forensic privacy self-audit layer.
* **Core Blueprints:**
  * Scans local browser runtimes for tracking nodes, proxy overrides, or unauthorized browser extension scraper bloat.
  * Calls low-level system checks on native Android/iOS mobile builds to flag kernel file modifications (Root/Jailbreak detection).
  * Executes completely on the client's local hardware and **never uploads a single byte of diagnostic data** to our servers.

---

## 📁 4. `src/core/` & `src/services/` — Shared Legal Logic & Security Anchors

### 📖 `regional_lexicon.py`
* **Role:** Multi-lingual constitutional and statutory heading dictionary database.
* **Core Blueprints:**
  * Pre-fills formal legal heading blocks across six major target languages: English, Malayalam, Kannada, Tamil, Hindi, and Assamese.
  * Contains the mandatory electronic-record acknowledgment templates linked to **Section 12(1) of the Information Technology Act, 2000**.

### 🛑 `legal_knowledge_guard.py`
* **Role:** Air-gapped input validation guardrail and anti-chat filter.
* **Core Blueprints:**
  * Enforces the anti-chat mandate by screening all raw user text against allowed civic keywords before it can reach the local AI engine.
  * Blocks conversational chatter, random searches, or general inquiries, and maps valid inputs to corresponding legal context blocks.

### 🔄 `reinforcement_loop.py`
* **Role:** Zero-trace user correction extractor for model style fine-tuning.
* **Core Blueprints:**
  * Intercepts manual text edits from citizens and removes proper nouns, dates, and locations to isolate pure phrasing styles.
  * Calculates abstract style changes (the difference between the AI's output and the user's edit) and caches them anonymously in the Redis pool for future air-gapped model training cycles.

### 🔑 `security_anchors.py`
* **Role:** Cryptographic trust anchor verification rules tracker.
* **Core Blueprints:**
  * Stores hardcoded cryptographic verification public keys (`npub`) for trusted community network nodes.
  * Validates incoming dynamic Nostr list events locally, allowing the application to update its municipal directories dynamically without relying on central database management.

---

## 📄 5. Documentation & Contributor Manuals

*   **`DEVELOPER_GUIDE.md`** — Core maintainer handbook detailing architectural requirements, local sandbox configurations, and strict zero-retention data policies.
*   **`CONTRIBUTING.md`** — Open-source developer onboarding manual specifying setup scripts (`setup_dev.sh`), Gitleaks pre-commit hooks, semantic branch commit formats, and the constitutional legal framework guidelines.
