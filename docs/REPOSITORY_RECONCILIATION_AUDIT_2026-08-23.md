# JANAVANI — REPOSITORY RECONCILIATION AUDIT

**Date:** 23 August 2026  
**Repository:** `netzen-abm/janavani`  
**Branch:** `main`  
**Mode:** READ-ONLY / NO CODE CHANGES  
**Purpose:** Reconcile the actual repository against the canonical Master Architecture, Master Task Checklist, Capability Registry and Data Contracts.

> This audit records what is observable in the repository. It does **not** declare runtime functionality complete merely because files or documentation exist. Runtime, deployment, integration and security claims require execution/testing evidence.

---

# 1. EXECUTIVE RESULT

## Overall assessment

**Repository condition: STRUCTURALLY RICH BUT ARCHITECTURALLY DIVERGENT.**

The repository already contains substantially more than the narrow MVP description in `README.md`. It contains:

- a Python application/core structure;
- Telegram, Web, WhatsApp and Messenger interface files;
- modular workflow/domain/service/document/storage layers;
- Rust protocol/decentralisation work;
- `janavani_v2` and `janavani_v3` parallel workspaces;
- database/static-data assets;
- extensive planning and architecture documentation;
- mesh/decentralisation-oriented material.

This is valuable work, but it creates a **convergence problem**: there are multiple architectural generations and multiple descriptions of the product in the same repository.

### Critical conclusion

**Do not delete `janavani_v2`, `janavani_v3`, legacy modules, or planning material yet.**

First establish:

```text
WHAT RUNS
   ↓
WHAT IS REFERENCED
   ↓
WHAT IS TESTED
   ↓
WHAT IS DEPLOYED
   ↓
WHAT IS CANONICAL
   ↓
WHAT IS EXPERIMENTAL
   ↓
WHAT IS ARCHIVE CANDIDATE
```

The next engineering phase should be **controlled convergence**, not another broad rewrite.

---

# 2. CANONICAL DOCUMENTS USED

The reconciliation target is:

1. `docs/JANAVANI_MASTER_ARCHITECTURE.md`
2. `docs/MASTER_TASK_CHECKLIST.md`
3. `docs/CAPABILITY_REGISTRY.md`
4. `docs/DATA_CONTRACTS.md`
5. Existing `docs/REPOSITORY_AUDIT.md`
6. Existing `README.md`
7. Existing planning contracts, especially:
   - `planning/DATABASE_CONTRACT.md`
   - `planning/DATABASE_DESIGN.md`
8. Actual repository paths visible on `main`.

The repository audit already establishes that old code should be verified before deletion and that storage, document generation, directory search and workflow responsibilities require reconciliation.

---

# 3. OBSERVED REPOSITORY TOPOLOGY

## 3.1 Root application structure

The root `src/` currently contains substantial modular structure including:

```text
src/
├── adapters/
├── app/
├── commands/
├── conversation/
├── core/
├── documents/
├── domain/
├── engine/
├── models/
├── services/
├── storage/
├── bot_telegram.py
├── bot_whatsapp.py
├── bot_messenger.py
├── main.py
├── legal_brain.py
└── lib.rs
```

This confirms that the repository is no longer accurately described as only a simple Telegram MVP codebase.

**Classification:** KEEP / RECONCILE.

---

# 4. MULTIPLE IMPLEMENTATION GENERATIONS

## 4.1 Root implementation

The root contains both Python and Rust artifacts. The root `Cargo.toml` explicitly defines optional decentralised protocol features including Freenet, Nostr, Nym, Reticulum, ZKP and blockchain-related dependencies.

**Finding:** The repository has already begun implementing the future decentralised architecture at the code/dependency level.

**Risk:** This is broader than the current README's MVP-first description and therefore needs a clear experimental/core boundary.

**Classification:** RETAIN / ARCHITECTURAL BOUNDARY REQUIRED.

## 4.2 `janavani_v2`

`janavani_v2/` is a separate workspace containing its own Rust project, source tree, tests, production mesh installation material and architecture documentation.

**Finding:** V2 is a parallel implementation generation, not merely a documentation folder.

**Classification:** RETAIN FOR RECONCILIATION; DO NOT DELETE.

## 4.3 `janavani_v3`

`janavani_v3/` is another separate Rust workspace, versioned `3.0.0`, using Dioxus with web/mobile/desktop features and its own source/test/deployment/documentation structure.

**Finding:** V3 is a second parallel implementation generation and is particularly relevant to the stated long-term Web/Android/iOS ecosystem.

**Classification:** RETAIN FOR RECONCILIATION; DO NOT DELETE.

### Required decision later

We must eventually establish one of:

```text
ROOT = canonical platform
V2/V3 = research/experimental
```

or

```text
V3 = canonical client/platform generation
ROOT = legacy/core services
```

or another evidence-based topology.

**This cannot be decided from filenames alone.**

---

# 5. README / PRODUCT-DIRECTION DRIFT

The current `README.md` describes a roadmap whose immediate focus is Web MVP and whose North Star is a reliable citizen problem → government-ready document workflow. It explicitly labels several decentralised technologies as deferred/future considerations.

However, the repository already contains:

- optional decentralised Rust protocol dependencies at root;
- a V2 workspace with production-mesh material;
- a V3 Dioxus workspace targeting web/mobile/desktop;
- WhatsApp and Messenger adapter files in root `src/`;
- broader governance/intelligence modules.

**Finding:** The README is not a reliable inventory of the actual repository contents.

This does **not** mean the README is wrong. It means it is an execution roadmap, while the repository contains experimental and future architecture alongside the current product.

**Action:** Later create a canonical repository-state document distinguishing:

- Core / production
- Current development
- Experimental
- Research
- Deprecated
- Archive candidate

**Classification:** DOCUMENTATION RECONCILIATION REQUIRED.

---

# 6. DATABASE / STORAGE RECONCILIATION

Existing planning documentation says the database should be a persistence boundary and that business logic belongs in services. `planning/DATABASE_CONTRACT.md` describes a minimal MVP data model, while `planning/DATABASE_DESIGN.md` describes a broader future database including citizens, issues, evidence, locations, departments, offices, documents, submissions, conversations and volunteers.

The actual repository currently contains:

```text
database/
├── complaints.jsonl
├── offices.csv
└── ratings.jsonl
```

The complaints file is empty and the ratings file contains only a minimal placeholder according to the repository listing.

There is also an established `src/storage/` directory.

### Finding

There are at least three conceptual persistence generations:

```text
database/ static files
        ↓
planning database design / Supabase concept
        ↓
src/storage/ canonical storage boundary
```

The new `DATA_CONTRACTS.md` is broader still.

### Decision

Do **not** migrate or delete database assets yet.

First map:

- imports;
- read/write paths;
- scripts;
- tests;
- deployment references;
- data ownership;
- migration requirements.

**Classification:** HIGH PRIORITY RECONCILIATION.

---

# 7. OFFICE / DIRECTORY DATA

The repository contains current service modules such as:

- `src/services/office_service.py`
- `src/services/search_directory.py`
- `database/offices.csv`

The existing repository audit also identifies historical directory-search code as a duplication risk.

The new Data Contracts require a richer `GovernmentOffice` model with:

- stable identity;
- organisation relationship;
- multiple addresses/contact points;
- official sources;
- verification status;
- verification timestamp.

### Gap

The existing static CSV model is materially narrower than the canonical data contract.

### Action

Create an **Office Data Migration/Verification Map** before changing the live lookup service.

**Classification:** INCOMPLETE / MIGRATION DESIGN REQUIRED.

---

# 8. DOCUMENT GENERATION

Observed repository components include:

- `src/documents/`
- `src/documents/generate_pdf.py`
- `src/documents/pdf_generator.py`
- `src/documents/complaint_builder.py`
- `src/services/document_service.py`

The repository audit already identifies document-generation duplication as an open technical-debt item.

The Data Contracts now require documents to support:

- To party;
- postal address;
- email;
- CC parties;
- references;
- enclosures/evidence;
- language;
- version;
- user approval;
- export/submission/archive state.

### Finding

The repository has significant document infrastructure, but the canonical document contract is broader than the legacy MVP contract.

### Action

Identify the single canonical document composition/generation path after import/runtime inspection.

**Classification:** IMPLEMENTATION PRESENT / CONTRACT ALIGNMENT REQUIRED.

---

# 9. ACCOUNTABILITY / GOVERNANCE MODULES

The repository already contains governance-oriented components such as:

- `src/services/rate_office.py`
- escalation modules;
- constitutional/legislative web routers;
- legal-brain components;
- land-related routers.

The new Capability Registry expands the governance domain substantially to include:

- office reviews;
- officer reviews;
- elected representative reviews;
- government performance indicators;
- transfer concerns;
- corruption reporting;
- misconduct reporting;
- whistleblower workflows.

### Finding

Some future ecosystem capabilities have already appeared in code, but their relationship to the current canonical capability model is not yet proven.

### Rule

**Existing code is evidence of implementation effort, not evidence of completion.**

Each module must be mapped to a capability ID and completion gate.

**Classification:** RECONCILE / DO NOT CLAIM COMPLETE.

---

# 10. MULTI-CHANNEL STATUS

Observed root interface files include:

```text
src/bot_telegram.py
src/bot_whatsapp.py
src/bot_messenger.py
src/web.py
```

The README describes Telegram as functional/frozen and Web as current priority, while WhatsApp and Messenger are part of the longer-term interface landscape.

### Finding

The repository contains adapters for multiple channels, but static presence does not establish production integration.

### Required evidence for each channel

```text
Adapter exists
   ↓
Configuration exists
   ↓
Credentials/secrets managed
   ↓
Local test
   ↓
Integration test
   ↓
Production endpoint
   ↓
Delivery acknowledgement
   ↓
Monitoring
```

**Classification:** PRESENT STRUCTURE / RUNTIME STATUS UNVERIFIED.

---

# 11. AI ARCHITECTURE

The repository contains AI/legal-oriented code, including `src/legal_brain.py` and `src/services/legal_agent.py`.

The canonical capability model now distinguishes:

- OCR;
- computer vision;
- RAG;
- SLM;
- LLM;
- agentic execution.

### Finding

Existing AI code should not automatically be treated as the canonical AI architecture.

### Required next step

Map every AI module to:

```text
Capability ID
Model/provider
Input contract
Output contract
Citation/provenance
Human approval gate
Fallback
Privacy boundary
Offline/local mode
Test coverage
```

**Classification:** PRESENT / ARCHITECTURE MAPPING REQUIRED.

---

# 12. EVIDENCE / BLOCKCHAIN / DECENTRALISATION

The repository already contains decentralised protocol-oriented Rust configuration at root and dedicated V2/V3 architecture material. The root `Cargo.toml` has optional features for Freenet, Nostr, Nym, Reticulum, ZKP and blockchain-related functionality.

The canonical capability/data model now defines blockchain as an **optional evidence/provenance anchoring mechanism**, not a universal dependency.

### Finding

The current repository is more decentralisation-oriented than the older README suggests.

### Canonical rule

```text
Evidence
  ↓
Canonical storage/provenance
  ↓
Optional hash anchor
  ↓
Blockchain / decentralised network
```

The core evidence system must continue to work if the external chain/network is unavailable.

**Classification:** STRATEGICALLY ALIGNED / IMPLEMENTATION STATUS UNVERIFIED.

---

# 13. MESH / SATELLITE SOS

The new capability registry establishes mesh and satellite SOS as architectural requirements rather than distant ideas.

The repository already contains mesh-related V2 material, including `install_production_mesh.sh`, indicating that mesh work has progressed beyond a purely conceptual document.

However, this audit has not yet established a verified end-to-end emergency delivery path.

### Required completion evidence

```text
SOS creation
 ↓
offline queue
 ↓
transport selection
 ↓
mesh/satellite adapter
 ↓
relay/gateway
 ↓
recipient
 ↓
acknowledgement
 ↓
truthful delivery status
```

**Classification:** ARCHITECTURE ALIGNED / END-TO-END STATUS UNVERIFIED.

---

# 14. ARCHIVE-FIRST POLICY

Existing repository audit rules already say old material must not be deleted merely because it appears obsolete.

The canonical direction is now stronger:

```text
KEEP
 ↓
REFACTOR
 ↓
MIGRATE
 ↓
DEPRECATE
 ↓
ARCHIVE
 ↓
DELETE ONLY WHEN JUSTIFIED
```

### Decision

No deletion is authorised by this audit.

Archive decisions should happen only after dependency, runtime, replacement and data-preservation checks.

**Classification:** LOCKED PRINCIPLE.

---

# 15. GAP MATRIX

| Area | Repository evidence | Canonical target | Status | Action |
|---|---|---|---|---|
| Core modular architecture | Strong | Capability-driven platform core | PARTIAL | Map modules |
| Telegram | Adapter + roadmap | Channel adapter | PRESENT / VERIFY | Runtime audit |
| Web | `src/web.py` + V3 web stack | Shared platform client | PRESENT / VERIFY | E2E audit |
| Android | V3 Dioxus target | Native/full client capability | DESIGN/PRESENT | Verify actual build |
| iOS | V3 Dioxus target | Native/full client capability | DESIGN/PRESENT | Verify actual build |
| WhatsApp | Adapter file | Production channel | UNVERIFIED | Integration audit |
| Messenger | Adapter file | Production channel | UNVERIFIED | Integration audit |
| DApp | Rust/decentralised material | Web3 interface | UNVERIFIED | Capability mapping |
| Workflow | Root modular layers + legacy history | Canonical workflow engine | PARTIAL | Dependency map |
| Storage | `src/storage/` + `database/` | Storage boundary | PARTIAL | Persistence audit |
| Office data | CSV + services | Versioned GovernmentOffice contract | INCOMPLETE | Migration map |
| Documents | Multiple generators/services | Canonical Document contract | PARTIAL | Reconcile generators |
| RTI | Roadmap/design | Full RTI capability | DESIGN | Implement after foundation |
| Schemes | Future/product docs | Source-grounded scheme service | DESIGN | Build later |
| Ratings | `rate_office.py`, JSONL | Evidence-aware reviews | PARTIAL | Contract mapping |
| Transfer concerns | Governance architecture | TransferConcern contract | DESIGN | Build later |
| Corruption | Governance architecture | Secure routing | DESIGN | Security-first design |
| Whistleblower | Architecture | High-risk secure case system | DESIGN | Threat model first |
| Experts/NGOs | Some volunteer architecture | ContributorProfile | PARTIAL | Contract mapping |
| OCR | AI roadmap | OCR capability | DESIGN | AI architecture |
| Computer Vision | AI roadmap | Vision capability | DESIGN | AI architecture |
| RAG | AI architecture | Grounded knowledge layer | DESIGN | Source registry |
| SLM | Local AI direction | Offline/local inference | DESIGN | Device matrix |
| LLM | Legal/AI code | Provider abstraction | PARTIAL | Model contract |
| Agent | Legal agent code | Tool-governed agent | PARTIAL | Safety gates |
| Evidence | Document/evidence work | EvidenceObject | PARTIAL | Provenance audit |
| Blockchain | Root optional dependency | Optional evidence anchor | PRESENT / VERIFY | Adapter test |
| Freenet | Root/V2 material | Optional decentralised transport | RESEARCH/EXPERIMENTAL | Keep isolated |
| Mesh | V2 mesh installer | SOS mesh transport | PRESENT / VERIFY | End-to-end test |
| Satellite | Architecture target | Satellite adapter | DESIGN | Regulatory/provider audit |
| SOS | Architecture | Multi-transport SOS | DESIGN/PARTIAL | Contract + transport work |
| Government alerts | Architecture | Authenticated alerts | DESIGN | Source/auth contract |
| Finance | New data contracts | Full transparency system | DESIGN | Governance/compliance design |
| Archive | Audit principle | Archive-first lifecycle | ALIGNED | Formal retention implementation |
| Testing | V2/V3 test directories + roadmap | Completion gate | PARTIAL | Run and record tests |
| Documentation | Extensive | One authoritative hierarchy | DRIFT | Reconcile |

---

# 16. HIGH-RISK ARCHITECTURAL ISSUES

## R-001 — Three implementation generations

**Severity:** HIGH

Root + V2 + V3 create a risk of building the same responsibility multiple times.

**Required control:** Canonical implementation map.

## R-002 — Python/Rust boundary unclear

**Severity:** HIGH

Both Python and Rust are present at root and in versioned workspaces.

**Required control:** Explicit language responsibility matrix.

## R-003 — Documentation/product-state mismatch

**Severity:** HIGH

README describes an MVP-centric roadmap while repository contents include broader platform experiments.

**Required control:** Repository State Register.

## R-004 — Persistence generations

**Severity:** HIGH

Static database files, planning database architecture and storage services coexist.

**Required control:** Data ownership + migration map.

## R-005 — Capability completion ambiguity

**Severity:** HIGH

Presence of a module does not equal a completed capability.

**Required control:** Capability ID + evidence + test + deployment gate.

## R-006 — Future technology leakage into core

**Severity:** MEDIUM/HIGH

Blockchain/decentralised components should remain optional adapters rather than becoming hard dependencies.

**Required control:** Adapter boundaries and feature flags.

---

# 17. WHAT IS ALREADY STRONGLY ALIGNED

The repository is not starting from zero. Strong alignment exists in these areas:

- modular separation of conversation/workflow/domain/services;
- interface independence as a stated principle;
- storage boundary concept;
- document layer;
- office search service direction;
- privacy-first philosophy;
- error/security/testing priorities;
- archive-before-delete philosophy;
- multi-interface direction;
- decentralisation experimentation;
- mesh experimentation;
- broader governance-service exploration.

The problem is primarily **convergence and verification**, not absence of architectural thinking.

---

# 18. WHAT MUST NOT HAPPEN NOW

Do not:

- delete V2;
- delete V3;
- delete legacy Python modules;
- rewrite the database;
- rewrite the workflow engine;
- replace the Telegram flow merely for architectural cleanliness;
- make blockchain mandatory;
- make one AI provider mandatory;
- implement every future capability simultaneously;
- mark a capability COMPLETE because a file exists;
- allow the new ecosystem documents to silently invalidate existing working code.

---

# 19. REQUIRED CONVERGENCE SEQUENCE

```text
STEP 1 — Repository State Register
        ↓
STEP 2 — Runtime / Import Map
        ↓
STEP 3 — Language Boundary Map
        ↓
STEP 4 — Storage Ownership Map
        ↓
STEP 5 — Capability → Module Map
        ↓
STEP 6 — Test / Deployment Evidence Map
        ↓
STEP 7 — Canonical Implementation Decisions
        ↓
STEP 8 — Migration Plans
        ↓
STEP 9 — Deprecation
        ↓
STEP 10 — Archive
        ↓
STEP 11 — Delete only when proven safe
```

No destructive cleanup should precede this sequence.

---

# 20. CURRENT DECISION

**The repository is NOT ready for a deletion/cleanup pass.**

**The repository IS ready for a controlled architecture-to-code mapping pass.**

This is the correct next engineering phase.

---

# 21. NEXT TWO AUDIT TASKS

### TASK A — Runtime / Import / Dependency Map

For every potentially duplicated responsibility, determine:

- who imports it;
- who calls it;
- what entry point reaches it;
- which tests cover it;
- which deployment references it;
- whether it is active, experimental or dead.

### TASK B — Capability → Repository Map

Create a machine-readable mapping:

```text
JNV-CIVIC-COMPLAINT
    → workflow modules
    → document modules
    → office services
    → storage
    → Telegram adapter
    → Web adapter
    → tests
    → deployment evidence
```

Repeat for every canonical capability.

---

# 22. AUDIT STATUS

**Repository audit:** COMPLETE FOR STATIC RECONCILIATION — 23 Aug 2026  
**Runtime audit:** NOT YET PERFORMED  
**Deletion authorisation:** NONE  
**Archive candidates:** NONE YET  
**Canonical architecture:** ACTIVE  
**Next phase:** RUNTIME / IMPORT / CAPABILITY MAPPING

**END OF AUDIT**
