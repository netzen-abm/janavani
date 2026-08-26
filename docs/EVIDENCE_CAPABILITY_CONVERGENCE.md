# Janavani Evidence Capability Convergence

**Status:** IMPLEMENTATION — boundary established; provider integration and repository-wide migration remain to be verified.
**Date:** 26 August 2026
**Scope:** shared ecosystem capability

## Authority

This document is subordinate to:

1. `docs/SOURCE_OF_TRUTH.md`
2. `docs/JANAVANI_MASTER_ARCHITECTURE.md`
3. `docs/CAPABILITY_REGISTRY.md`
4. `docs/DATA_CONTRACTS.md`
5. `docs/MASTER_TASK_CHECKLIST.md`

It records the implementation decision for the shared evidence/provenance boundary; it does not replace those documents.

## Purpose

Evidence is a cross-ecosystem capability used by civic workflows, documents, accountability, AI/RAG, device-security observations and future decentralized anchoring.

The capability must remain channel-neutral and provider-neutral.

```text
Web / Telegram / Android / iOS / DApp / API / other interfaces
                              |
                              v
                    EvidenceCapability
                              |
                    +---------+---------+
                    |                   |
                    v                   v
               EvidenceStore     ProvenanceRecorder
                    |                   |
                    +---------+---------+
                              v
                  EvidenceItem + Provenance
```

## Core rule

**Evidence is captured and described; it is not automatically declared true.**

An evidence adapter, storage provider, OCR system, AI model or device-security adapter must not silently convert an observation into a verified factual finding.

## Contract

`src/capabilities/evidence_capability.py` defines:

- `EvidenceItem` — channel-neutral evidence metadata and optional content hash.
- `EvidenceProvenance` — source, capture time, transformations and integrity metadata.
- `EvidenceStore` — provider-neutral persistence boundary.
- `ProvenanceRecorder` — provider-neutral provenance boundary.
- `EvidenceCapability` — reusable orchestration boundary.

## Alignment with canonical data contracts

`docs/DATA_CONTRACTS.md` requires stable identifiers, provenance where practical, explicit distinction between user-generated claims and verified facts, UTC timestamps internally, schema/version discipline, privacy minimisation, and capability contracts rather than channel-specific internal objects. The capability follows those rules without introducing a competing data model.

## Failure behavior

The capability must fail truthfully:

- If evidence cannot be stored, do not report it as safely persisted.
- If provenance cannot be recorded, expose that limitation to the caller.
- If a hash is unavailable, do not manufacture one.
- If an external anchor is unavailable, ordinary evidence operation must remain possible where the selected storage policy permits.
- If AI/OCR/CV processing fails, preserve the original evidence path where practical.

## Privacy and safety

Implementations must follow the ecosystem privacy and safety invariants in `SOURCE_OF_TRUTH.md`: minimum necessary collection, purpose limitation, consent, identity minimisation, access control, secure evidence handling, retention controls and auditability.

## Implementation boundary

This convergence step intentionally does **not** implement:

- a new database schema;
- a new object-storage provider;
- blockchain/IPFS anchoring;
- OCR/CV/VLM processing;
- legal or factual verification;
- automatic evidence scoring.

Those are separate adapters/capabilities and require their own contracts and verification.

## Verification gates

Before marking the capability `COMPLETE`:

1. Unit tests cover valid and invalid evidence metadata.
2. Contract tests cover store/provenance adapters.
3. Existing complaint/document/evidence consumers are traced and migrated where appropriate.
4. Storage ownership is reconciled against `docs/STORAGE_OWNERSHIP_MAP_2026-08-23.md`.
5. Privacy/security behavior is tested.
6. Deployment/runtime imports are verified.
7. `docs/CAPABILITY_REGISTRY.md` is updated from `DESIGN` to the appropriate verified state only after evidence exists.

## Non-goals

Do not create parallel evidence implementations merely to match the architecture tree. The canonical boundary should be adopted incrementally and old implementations should be archived only after dependency and runtime verification.
