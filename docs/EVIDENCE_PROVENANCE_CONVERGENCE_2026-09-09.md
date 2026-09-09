# Janavani — Evidence + Provenance Convergence

**Date:** 9 September 2026  
**Status:** VERIFYING  
**Scope:** Canonical Evidence + Provenance boundary for the complete Janavani ecosystem.

## Decision

Janavani already contained the strongest current Evidence domain contract in `src/core/evidence.py` and provider-neutral metadata repository boundary in `src/storage/repositories/evidence.py`. The convergence work therefore extends those contracts rather than creating a second evidence model.

The canonical Evidence boundary is now `src/capabilities/evidence.py`.

## Canonical boundary

`EvidenceCapability` provides:

- registration of evidence metadata;
- canonical SHA-256 validation/normalisation;
- provenance preservation through `EvidenceSource`;
- attachment of registered evidence to an owned Case;
- owner-scoped evidence metadata retrieval;
- authorization at the shared capability boundary;
- storage-reference semantics rather than binary content inside the domain object.

Registration does **not** upload, transmit, or publish the evidence artifact. A `storage_ref` identifies where the artifact is held; the capability itself remains provider- and surface-neutral.

## Existing provider boundaries retained

- `src/core/evidence.py` remains the domain contract.
- `src/storage/repositories/evidence.py` remains the local/in-memory provider.
- `src/storage/repositories/postgres_evidence.py` remains the PostgreSQL metadata provider.
- Binary artifact storage remains outside the Evidence domain object.

No provider was promoted to domain authority.

## Security and privacy posture

- Evidence registration requires the shared `case:evidence` capability.
- Evidence attachment requires an existing registered evidence object and an owned Case.
- Cross-owner Case access fails closed.
- Evidence content is never implicitly transmitted by registration or attachment.
- The Case stores an evidence reference, not the binary artifact.
- Provenance and integrity metadata travel with the EvidenceObject contract.

## Submission convergence correction

During this pass, the submission boundary was re-verified. `src/capabilities/submission.py` had attempted to persist a transport failure through an object-identity-sensitive `save_owned` path. That was unnecessary because `case:begin_submission` already persists `SUBMITTING` before external I/O. The failure path was therefore simplified so durable providers do not depend on in-memory object identity.

## Verification status

Focused repository tests were added in `tests/test_evidence_capability.py`, covering registration, hash/provenance preservation, attachment, owner isolation, missing evidence, and authorization failure.

The existing `tests/test_submission_capability.py` was re-read after the correction. It covers explicit approval, consent, transport failure without false success, acknowledgement, and the separation of document generation from submission.

**Important:** GitHub Actions execution for the new commits has not yet been independently confirmed. Therefore this work is **VERIFYING**, not COMPLETE.

## Next convergence gate

1. Obtain CI evidence for the current `main` commits.
2. Connect Evidence + Provenance to the complete Case → Authority → Document vertical slice without creating a second evidence implementation.
