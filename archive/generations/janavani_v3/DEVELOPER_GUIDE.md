# 🏛️ Janavani V3 — Core Developer Manual & System Playbook

This document details the architectural boundaries, dependency configurations, and internal security guidelines required to maintain the Janavani V3 sovereign citizen engine.

## 🛠️ Complete Project Topology Index

The platform uses a modular, decoupled structure to ensure zero fault propagation across communication channels:

```text
janavani_v3/
├── Cargo.toml                     <-- Master Project Configuration
├── Dioxus.toml                    <-- Cross-Platform Build Manifest
├── nginx.conf                     <-- Secure Public Reverse Proxy Firewall
├── deploy_production.sh           <-- Blue-Green Rolling Deployment Orchestrator
├── run_all_tests.sh               <-- Multi-Language Verification Harness
└── src/
    ├── main.rs                    <-- Isomorphic Rust SPA Interface Hub (Dioxus)
    ├── capability.rs              <-- Device Hardware Resource Profiler
    ├── auto_transport.rs          <-- Invisible Network Middleware Sensing Core
    ├── web/
    │   ├── app.py                 <-- Ingestion FastAPI Core API (Stateless)
    │   ├── land_router.py         <-- Cadastral Record & Revenue Matrix Proxy
    │   └── de_linked_ingestion.py <-- Multi-Modal Asset Shredding Dissector
    └── core/
        ├── regional_lexicon.py    <-- Multi-Lingual Preamble Headings Database
        └── security_anchors.py    <-- Cryptographic Nostr Trust Key Anchors
```

---

## 🔒 Mandatory Core Architectural Invariants

### 1. In-Memory Transient Cache Pipeline (Zero Persistent Storage Logs)
The platform is built to maintain zero persistent data records on physical storage media across its ingestion pipelines. 
* All transaction tracking payloads, active ratings tokens, and user document segments must be cached strictly inside **volatile Redis in-memory clusters with a maximum 30-minute sliding window Time-To-Live (TTL)**.
* Databases (SQL/NoSQL) are forbidden in the ingestion pipeline to prevent long-term data leaks.

### 2. Multi-Tier Anti-Chat Knowledge Guardrails
Janavani is exclusively an automated legal document formatting engine; it is **not** an open conversational chatbot or general-purpose web search engine.
* Every text string input must pass through the `AirGappedKnowledgeGuardrail` script before hitting the local SLM sandbox.
* Any request containing casual chatter, conversational loops, or out-of-scope queries must be blocked instantly at the API gateway layer.

### 3. Local Air-Gapped Model Isolation (Privacy Shield)
* Direct connections to external cloud language models are strictly blocked in production.
* The processing backend routes requests exclusively over internal network bridges to an isolated **Ollama container sandbox hosting a localized, quantized Llama-3-8B model**. This prevents user text context from leaking to third-party servers.

---

## 🧪 Operational Quality Testing Framework

Before any code updates can be merged into production branches, they must pass the central testing suite cleanly. Run this verification command locally on your workspace node:

```bash
chmod +x run_all_tests.sh
./run_all_tests.sh
```

The script runs automated checks covering multi-lingual parsing consistency, local geodetic coordinate conversion math, token blacklisting lifecycles, and cryptographic signature validation routines across directories.
