# JANAVANI — STORAGE OWNERSHIP MAP

**Date:** 23 August 2026  
**Phase:** M2-D  
**Mode:** READ-ONLY RECONCILIATION  
**Repository:** `netzen-abm/janavani`

> This document maps the storage mechanisms actually present in the repository against the canonical ecosystem data model. It does not migrate data or change runtime behavior.

---

# 1. EXECUTIVE FINDING

Janavani currently has **multiple persistence mechanisms with overlapping responsibility**:

```text
CSV
JSONL
Supabase/PostgreSQL
Redis
FAISS / RAG storage
runtime/cache
```

The repository's older database contract explicitly says the database stores data only and business logic belongs in services/repositories. fileciteturn341file0

The broader database design identifies Supabase/PostgreSQL as the intended scalable database and includes citizens, issues, evidence, locations, departments, offices, documents, submissions, conversations and volunteers. fileciteturn342file0

Therefore the correct direction is **not** to add more persistence systems. It is to establish one canonical durable-data authority and retain specialised stores only where their technical role requires them.

---

# 2. CANONICAL STORAGE PRINCIPLE

The recommended target is:

```text
                 JANAVANI DATA DOMAIN
                         │
                         ▼
              Canonical Data Contracts
                         │
                         ▼
              Repository / Data Access Layer
                         │
          ┌──────────────┼──────────────┐
          ▼              ▼              ▼
      PostgreSQL      Object Store    Event/Queue
      (durable)       (documents)     (delivery)
          │
          └──────────────┐
                         ▼
                  Audit / Archive

Specialised stores remain adapters:

Redis  → ephemeral state/cache/queue
FAISS  → derived RAG index
Blockchain → optional evidence anchor
Mesh/Satellite → transport, NOT database
```

---

# 3. CURRENT STORAGE INVENTORY

## S-01 — `database/offices.csv`

**Current owner:** `database/` static data  
**Used by:** `src/services/search_directory.py`  
**Data:** office ID, name, type, address, city, officer role, email. fileciteturn345file0

**Role:** Development/static directory seed.

**Canonical status:** LEGACY SEED / MIGRATION SOURCE.

**Why:** The canonical `GovernmentOffice` contract requires substantially more provenance, organisation, jurisdiction, contacts and verification metadata.

**Do not delete:** This is a useful seed/source until migration is complete.

---

## S-02 — `database/complaints.jsonl`

**Current owner:** filesystem  
**Writer:** `src/services/storage_service.py`  
**Data:** complaint ID, issue, category, department, district, office, created timestamp and status. fileciteturn349file0

Current file is empty. fileciteturn346file0

**Role:** Current local persistence for complaint records.

**Canonical status:** LEGACY LOCAL STORE / MIGRATION SOURCE.

**Gap:** It lacks the broader complaint lifecycle, citizen/consent relationship, evidence, document, submission, provenance, audit and archive model.

---

## S-03 — `database/ratings.jsonl`

**Current owner:** filesystem  
**Writer:** `src/services/rate_office.py`  
**Data:** rating, issue, office, hashed user phone, timestamp and status. fileciteturn351file0

Current repository file is empty. fileciteturn347file0

**Role:** Current local rating/complaint persistence.

**Canonical status:** LEGACY LOCAL STORE / MIGRATION SOURCE.

**Important issue:** The code calls the record a complaint while storing it in `ratings.jsonl`. This is a domain-boundary inconsistency that should be resolved in the future canonical data model.

---

## S-04 — Supabase/PostgreSQL

`src/storage/supabase.py` creates a Supabase client when URL and anonymous key configuration are available. fileciteturn344file0

The planning database design explicitly identifies Supabase/PostgreSQL as the intended scalable database and already defines a broad normalized entity model. fileciteturn342file0

**Canonical status:** TARGET DURABLE DATA AUTHORITY — SUBJECT TO RUNTIME VERIFICATION.

**Required next work:** schema inspection, migrations, repositories/data-access layer, row-level security, backup/recovery and integration tests.

---

## S-05 — Redis

**Observed role:** runtime/ephemeral state and emergency/agent-related operations.

**Canonical status:** SPECIALISED EPHEMERAL STORE.

**Rule:** Redis must not become the authoritative store for durable citizen records, evidence, complaints, finance or governance records.

---

## S-06 — FAISS / RAG index

**Observed role:** retrieval index for RAG proof-of-concept.

**Canonical status:** DERIVED KNOWLEDGE INDEX.

**Rule:** FAISS is not the source of truth. Every retrieved knowledge object must trace back to canonical source documents/records and provenance metadata.

---

## S-07 — In-memory/runtime cache

**Observed in:** application services.

**Canonical status:** EPHEMERAL.

**Rule:** Never treat cache contents as durable citizen/evidence state.

---

# 4. DOMAIN OWNERSHIP TARGET

| Domain object | Current storage | Canonical owner | Status |
|---|---|---|---|
| Citizen identity | temporary / scattered | PostgreSQL identity boundary | DESIGN |
| Consent | scattered | PostgreSQL consent records | DESIGN |
| Government organisation | CSV/planning | PostgreSQL | MIGRATION TARGET |
| Government office | CSV | PostgreSQL | MIGRATION TARGET |
| Office contacts | CSV | PostgreSQL normalized contacts | DESIGN |
| Address verification | not canonical | PostgreSQL + audit history | DESIGN |
| Complaint | JSONL | PostgreSQL | MIGRATION TARGET |
| Complaint evidence | partial/file layer | PostgreSQL metadata + object storage | DESIGN |
| Rating | JSONL | PostgreSQL | MIGRATION TARGET |
| Officer/representative review | emerging | PostgreSQL | DESIGN |
| Document metadata | document layer | PostgreSQL | DESIGN |
| Document binary | filesystem/generator | Object storage | DESIGN |
| Submission | emerging | PostgreSQL | DESIGN |
| Conversation state | runtime | Redis/session + durable audit where required | PARTIAL |
| Whistleblower case | not established | isolated secure database/object store | DESIGN |
| Contributor profile | emerging | PostgreSQL | DESIGN |
| Financial contribution | not established | PostgreSQL + immutable audit ledger | DESIGN |
| SOS case | Redis/runtime + future event layer | PostgreSQL case + ephemeral transport state | DESIGN |
| SOS delivery event | transport-specific | event/queue + audit | DESIGN |
| Emergency government alert | not established | PostgreSQL + signed event log | DESIGN |
| Knowledge source | RAG POC | PostgreSQL/source registry + object storage | DESIGN |
| RAG index | FAISS | derived index | POC |
| Evidence hash | security/provenance layer | PostgreSQL audit + optional blockchain anchor | PARTIAL |
| Archive record | not unified | PostgreSQL archive metadata + object storage | DESIGN |

---

# 5. DATA CONTRACT RECONCILIATION

The old database contract is intentionally small: offices, citizens, complaints and ratings, with business logic outside the database. fileciteturn341file0

The broader database design already anticipates a multi-channel platform with evidence, documents, submissions, conversations and volunteers. fileciteturn342file0

The new ecosystem data contracts extend this further into:

- consent;
- verification;
- evidence provenance;
- address correction;
- whistleblower cases;
- contributor disclosure preferences;
- finance transparency;
- SOS;
- mesh/satellite delivery;
- government alerts;
- AI/RAG provenance;
- archive lifecycle.

### Conclusion

We should **version and evolve the database contract**, rather than trying to force the MVP contract to represent the entire ecosystem.

---

# 6. STORAGE RULES TO LOCK

## Rule 1 — One durable source of truth

PostgreSQL/Supabase should become the authoritative relational source for durable platform records, subject to schema/security verification.

## Rule 2 — Object storage for binary evidence

PDFs, DOCX, images, OCR artifacts and other large files should not be stored as ordinary relational fields unless there is a specific reason.

## Rule 3 — Redis is ephemeral

Session, queue, rate-limit, temporary workflow and transport state may use Redis.

## Rule 4 — RAG index is derived

Never allow FAISS/vector storage to become the authoritative legal/government knowledge source.

## Rule 5 — Blockchain is optional anchoring

Store the evidence/provenance record first; anchor its cryptographic digest externally when required.

## Rule 6 — Transport is not storage

Telegram, WhatsApp, Messenger, mesh and satellite are delivery channels. They must not become canonical data stores.

## Rule 7 — Archive is a state, not deletion

Records that leave active operational use should move through the archive lifecycle while retaining required provenance and retention controls.

---

# 7. MIGRATION PRINCIPLE

Do not perform a big-bang database rewrite.

Use:

```text
Current store
    ↓
Inventory
    ↓
Canonical schema mapping
    ↓
Migration script
    ↓
Validation
    ↓
Dual-read / controlled cutover where needed
    ↓
Canonical PostgreSQL ownership
    ↓
Legacy store read-only
    ↓
Archive
```

For the current repository, the JSONL files are presently empty, so migration risk is low for those specific files, but the code paths still need replacement and test coverage before the files can be retired.

---

# 8. SECURITY / PRIVACY REQUIREMENTS

The durable storage architecture must support:

- encryption at rest where provided by the infrastructure;
- least-privilege database roles;
- row-level authorization;
- consent records;
- immutable audit events where appropriate;
- sensitive-case isolation;
- retention schedules;
- legal hold;
- archive state;
- deletion/anonymisation rules where legally required;
- access logging;
- administrator accountability.

Whistleblower and sensitive SOS data require stronger isolation than ordinary public complaints.

---

# 9. IMMEDIATE REPOSITORY FINDINGS

### Finding F-01

The repository currently has both a static CSV directory and a Supabase client. This is not automatically wrong, but their ownership is currently ambiguous.

### Finding F-02

Complaint persistence currently writes directly to a JSONL file from a service. This bypasses the intended repository/data-access abstraction described by the database contract. fileciteturn341file0 fileciteturn349file0

### Finding F-03

Ratings are written to a file called `ratings.jsonl`, but the implementation describes the generated record as a complaint and returns a complaint ID. fileciteturn351file0

### Finding F-04

The current CSV office schema is a seed dataset, not sufficient as the final GovernmentOffice data model. fileciteturn345file0

### Finding F-05

The existing planning database design is already much closer to the ecosystem direction than the older MVP database contract. fileciteturn342file0

---

# 10. NO DELETION / ARCHIVE DECISION

No storage file is approved for deletion by this document.

Potential future archive candidates:

```text
database/offices.csv
 database/complaints.jsonl
 database/ratings.jsonl
```

But only after:

1. canonical schema exists;
2. migration is complete;
3. all code references are removed/replaced;
4. tests pass;
5. production runtime is confirmed;
6. historical data preservation is verified;
7. rollback is available;
8. archive copy is created.

---

# 11. NEXT PHASE — M3 VERIFICATION

The storage map is now sufficiently defined to move to execution verification.

### M3-A
Run the repository's actual test suites and classify:

- pass;
- fail;
- skipped;
- environment failure;
- dependency failure;
- external-service failure;
- security blocker.

### M3-B
Verify each declared deployment path:

```text
Render
Docker
entrypoint.sh
Web/API
Telegram
```

### M3-C
Record the evidence in the master task checklist status register.

---

# 12. STATUS

**M2-D Storage Ownership Map:** COMPLETE FOR STATIC RECONCILIATION  
**Data migration:** NOT STARTED  
**Runtime verification:** NEXT  
**Destructive changes:** NONE  
**Archive approvals:** NONE  

**END OF DOCUMENT**
