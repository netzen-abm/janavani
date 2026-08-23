# JANAVANI — MASTER TASK CHECKLIST RECONCILIATION

**Date:** 23 August 2026
**Purpose:** Reconcile the canonical Master Task Checklist against verified repository evidence without silently rewriting historical status.

## 1. Why this file exists

The canonical `docs/MASTER_TASK_CHECKLIST.md` is the master task inventory. The dated status register records verified progress. A reconciliation pass found that several checkboxes in the canonical checklist had not yet been synchronized with evidence already recorded in the status register.

This document is the control record for that mismatch. It prevents duplicate audits and prevents a design task that is already documented from being treated as if it has never been done.

## 2. Verified synchronization findings

### Master Task 1 — Architecture & System Governance

Already verified:

- 1.1 Master architecture exists.
- 1.2 Capability-first architecture locked.
- 1.3 Independent-channel principle locked.
- 1.4 AI/non-AI independence locked.
- 1.5 Mesh is a current SOS capability.
- 1.6 Satellite is a current SOS capability.
- 1.7 Archive-over-delete principle locked.

Also already evidenced but not synchronized in the canonical checklist:

- 1.8 Capability registry exists: `docs/CAPABILITY_REGISTRY.md`.
- 1.9 Core data contracts exist: `docs/DATA_CONTRACTS.md`.

These are **DESIGN COMPLETE**, not implementation complete.

Still unresolved:

- 1.10 Permission/consent contracts.
- 1.11 Transport abstraction contracts.
- 1.12 Failure/dependency matrix.
- 1.13 System-wide threat model.
- 1.14 System-wide test strategy.

### Master Task 2 — Repository Baseline & Architecture Reconciliation

Verified from prior audits:

- 2.1 Static repository/tree inventory — complete.
- 2.4 Static storage inventory — complete.
- 2.6 Static decentralized inventory — complete.
- 2.9 Static implementation-vs-architecture comparison — complete as a static audit.
- 2.10 Preliminary duplicate/obsolete identification — complete as a static audit.
- 2.12 Architecture-gap report — complete.

The following remain open because they require runtime/deployment evidence:

- 2.2 Live runtime entry-point verification.
- 2.3 Runtime API/service execution inventory.
- 2.5 Runtime AI integration verification.
- 2.7 Runtime SOS execution verification.
- 2.8 Test/CI execution evidence inventory.
- 2.9 Runtime comparison against Master Architecture.
- 2.10 Runtime confirmation of duplicates/obsolete code.
- 2.11 Archive decisions after dependency/replacement verification.

### Master Task 3 — Capability Registry

Verified design completion:

- `docs/CAPABILITY_REGISTRY.md` exists.
- Capability ID convention is defined.
- Capability metadata fields are defined.
- Civic, government, accountability, evidence, expert/volunteer, SOS and financial capability families are registered.

Remaining: repository-module, test, deployment, security/privacy and evidence mapping for each capability.

### Master Task 4 — Core Data Contracts

Verified design completion:

- `docs/DATA_CONTRACTS.md` exists.
- Identity, consent, preference, case, office, officer, representative, scheme, document, address, evidence, provenance, expert review, correction, SOS, alert, financial and archive/retention contracts are defined.

Remaining: implementation mapping and storage ownership validation. No database migration is authorised merely because the contract exists.

## 3. Current execution phase

**M2 — Repository Runtime / Dependency Reconciliation**

Static mapping is substantially complete. The next work is not another generic repository audit.

The next unresolved work is:

1. M2-B — Capability → Repository → Test → Deployment Map.
2. M2-C — Storage Ownership Map (reconnaissance already performed; ownership decisions still require verification).
3. M2-D — Runtime Execution Verification.

## 4. Storage reconnaissance already completed

The 23 August storage reconnaissance established the following important facts:

- Local durable data exists in `database/complaints.jsonl`, `database/offices.csv`, and `database/ratings.jsonl`.
- Canonical storage modules exist under `src/storage/`.
- Redis is used extensively as a transient/volatile layer in the main, V2 and V3 paths.
- Supabase integration exists but is not sufficient evidence of canonical runtime ownership.
- V2/V3 contain separate Redis-backed paths.
- Several legacy and duplicate storage paths remain.

**Decision:** do not migrate, delete, merge or rename storage until the runtime ownership map is complete.

## 5. Documentation-control rule

Before beginning a new audit:

1. Check `MASTER_TASK_CHECKLIST.md`.
2. Check the latest `MASTER_TASK_CHECKLIST_STATUS_<DATE>.md`.
3. Check existing dated audit evidence.
4. Audit only the unresolved delta.
5. Record new evidence in a dated document.
6. Update the checklist/status record.

This is specifically intended to prevent repeating the same audit.

## 6. Ecosystem scope lock

Janavani is **not an MVP project**.

The product target is the complete citizen-governance ecosystem, including the capability layer and independently replaceable interfaces for:

- Dynamic Web application.
- Android application.
- iOS application.
- Telegram Bot.
- Telegram Mini App.
- WhatsApp integration.
- Messenger integration.
- Web3/DApp capability.
- Internet transport.
- Mesh/resilient transport.
- Satellite/resilient transport where legally and technically supported.
- Decentralized storage/transport evaluation.
- AI and non-AI operating paths.

Individual milestones are construction and verification stages, not the final product boundary.

## 7. Archive rule

No document, source directory, runtime, or implementation is to be archived solely because it appears old or duplicated.

Archive requires:

- dependency verification;
- runtime verification;
- replacement identification;
- data preservation assessment;
- test verification;
- historical-value assessment;
- explicit archive record.

## 8. Next action

Proceed to **M2-B — Capability → Repository → Test → Deployment Map**.

Do not repeat the completed static repository inventory, capability-registry design, data-contract design, or storage reconnaissance except where new evidence requires reconciliation.
