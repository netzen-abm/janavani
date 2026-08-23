# JANAVANI — MASTER TASK CHECKLIST RECONCILIATION

**Date:** 23 August 2026  
**Purpose:** Reconcile the canonical Master Task Checklist against verified repository evidence and prevent duplicate audits.

## 1. CONTROL RULE

`docs/MASTER_TASK_CHECKLIST.md` is the authoritative task inventory.  
`docs/MASTER_TASK_CHECKLIST_STATUS_2026-08-23.md` is the dated evidence/status register.  
Dated audits are evidence records, not competing task lists.

Before any new audit:

1. Read `docs/DOCUMENTATION_INDEX.md`.
2. Read `docs/MASTER_TASK_CHECKLIST.md`.
3. Read the latest status register.
4. Read only the relevant dated audits.
5. Identify the unresolved delta.
6. Audit only that delta.
7. Record new evidence and update the checklist/status register.

## 2. VERIFIED ARCHITECTURE / DOCUMENTATION FOUNDATIONS

Already evidenced:

- Master architecture exists.
- Capability-first architecture is locked.
- Independent-channel principle is locked.
- AI/non-AI independence is locked.
- Mesh and satellite are defined as SOS capabilities.
- Archive-over-delete is locked.
- `docs/CAPABILITY_REGISTRY.md` is DESIGN COMPLETE.
- `docs/DATA_CONTRACTS.md` is DESIGN COMPLETE.
- Ecosystem identity is locked as a full citizen-governance ecosystem, not an MVP.
- README and ROADMAP have been reconciled with that scope.
- Documentation authority/index and correction rules exist.
- Canonical API assembly is `src/web/canonical_app.py`.

## 3. VERIFIED STATIC REPOSITORY EVIDENCE

Already evidenced; do not repeat as generic audits:

- Static repository/tree inventory.
- Static storage/database inventory.
- Static decentralized-component inventory.
- Static implementation-vs-architecture comparison.
- Preliminary duplicate/obsolete identification.
- Static architecture-gap report.
- Runtime/import/dependency mapping.
- Deployment topology mapping.
- Capability → repository → test → deployment static mapping.
- Storage ownership reconnaissance/design mapping.
- Canonical API route ownership mapping.
- Canonical API assembly/legacy isolation structural verification.

These records remain the evidence base. Re-open only when a new code/document change materially changes the evidence.

## 4. OPEN MASTER TASK 1 — ARCHITECTURE & SYSTEM GOVERNANCE

**Status: IN PROGRESS**

Remaining:

- [ ] 1.10 Permission/consent contracts.
- [ ] 1.11 Transport abstraction contracts.
- [ ] 1.12 Failure/dependency matrix.
- [ ] 1.13 System-wide threat model.
- [ ] 1.14 System-wide test strategy.

## 5. OPEN MASTER TASK 2 — RUNTIME / DEPENDENCY RECONCILIATION

**Status: IN PROGRESS — STATIC MAPPING COMPLETE; LIVE VERIFICATION OPEN**

Remaining:

- [ ] 2.2 Live runtime entry-point verification.
- [ ] 2.3 Runtime API/service execution inventory.
- [ ] 2.5 Runtime AI integration verification.
- [ ] 2.7 Runtime SOS execution verification.
- [ ] 2.8 Test/CI execution evidence inventory.
- [ ] 2.11 Archive obsolete material only after dependency/replacement/runtime verification.

Additional convergence note:

- `src/web/canonical_app.py` is the canonical API assembly boundary.
- This does **not** yet prove the canonical production runtime.
- `src/web.py`, `src/web/app.py`, `src/main.py`, and `src/web_mvp/main.py` remain runtime/legacy candidates until actual deployment ownership is verified.
- `src/web.py` contains historical Web→Telegram process coupling; this is a P0 runtime/deployment verification item, not an immediate deletion target.

## 6. MASTER TASK 3 — CAPABILITY REGISTRY

**Status: DESIGN COMPLETE — STATIC IMPLEMENTATION MAPPING COMPLETE; RUNTIME VERIFICATION PENDING**

Evidence:

- `docs/CAPABILITY_REGISTRY.md`
- `docs/CAPABILITY_REPOSITORY_TEST_DEPLOYMENT_MAP_2026-08-23.md`

## 7. MASTER TASK 4 — CORE DATA CONTRACTS

**Status: DESIGN COMPLETE — STORAGE OWNERSHIP MAPPED; IMPLEMENTATION MIGRATION PENDING**

Evidence:

- `docs/DATA_CONTRACTS.md`
- `docs/STORAGE_OWNERSHIP_MAP_2026-08-23.md`

No destructive storage migration is authorised merely because contracts exist.

## 8. DOCUMENTATION CONVERGENCE

**Status: IN PROGRESS**

The canonical chain is:

```text
North Star
↓
Ecosystem Charter
↓
Source of Truth
↓
Master Architecture
↓
Product Landscape
↓
Roadmap
↓
Capability Registry / Data Contracts / planning contracts
↓
Master Checklist + Status Register
↓
Actual implementation / tests / CI / deployment evidence
```

The repository has already corrected the major MVP-era product-boundary ambiguity. Remaining documentation work is controlled classification and reconciliation of supporting contracts, V2/V3 records, deployment/developer/contribution documents and remaining root-level material.

Historical audits must not be rewritten merely to remove old observations. Their current interpretation is governed by the canonical hierarchy and `docs/DOCUMENTATION_CORRECTION_NOTICE_2026-08-23.md`.

## 9. STORAGE CONTROL

Storage reconnaissance has already established:

- `database/complaints.jsonl`
- `database/offices.csv`
- `database/ratings.jsonl`
- `src/storage/` repository/cache/Supabase modules
- Redis transient-storage usage across main/V2/V3
- Supabase integration
- legacy/parallel storage paths

Decision: no migration, deletion, merge or rename until runtime ownership is verified.

## 10. CURRENT EXECUTION GATE

The next engineering work is **not another broad audit**.

The immediate unresolved gate is:

```text
M3-A — actual CI/test execution evidence
        ↓
M3-B — runtime/deployment ownership verification
        ↓
M3-C — channel integration/runtime verification
        ↓
targeted convergence of proven boundaries
        ↓
full ecosystem capability construction
```

The broader ecosystem remains the destination. Any Web citizen-flow work is a construction milestone inside that ecosystem, not an MVP product boundary.

## 11. ARCHIVE CONTROL

No archive operation is authorised merely because a document or code path is old, duplicated, experimental or superseded-looking.

Archive requires:

1. no active dependency;
2. no required runtime path;
3. no irreplaceable data;
4. replacement where required;
5. test/runtime verification where applicable;
6. historical value preserved;
7. archive reason recorded.

**END — RECONCILIATION CONTROL RECORD**
