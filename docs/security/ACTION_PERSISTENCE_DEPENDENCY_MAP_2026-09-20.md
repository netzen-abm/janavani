# Action → Persistence Dependency Map

**Date:** 20 September 2026  
**Status:** Security/architecture conformance baseline

This document traces registered application actions through active capability methods to their persistence boundaries. It is deliberately evidence-based: an action is marked GAP where the active code does not expose enough information to establish a safe database/RLS mapping.

| Action | Capability entry | Persistence path | Tables / surfaces | Transaction | RLS mapping |
|---|---|---|---|---|---|
| create | CivicCaseCapability.create | CivicCaseRepository.save | civic_cases + case_events + refs | repository/UoW dependent | owner INSERT |
| save | CivicCaseCapability.save_owned | CivicCaseRepository.save | civic_cases + child projections | repository/UoW dependent | owner UPDATE |
| case:add_evidence | CivicCaseCapability.add_evidence | CivicCaseRepository.save | civic_cases + case_events + evidence refs | repository/UoW dependent | owner-only candidate; child INSERT must not exceed Case authorization |
| case:add_document | CivicCaseCapability.add_document | CivicCaseRepository.save | civic_cases + case_events + document refs | repository/UoW dependent | owner-only candidate; child INSERT must not exceed Case authorization |
| case:start_review | CivicCaseCapability.transition | CivicCaseRepository.save | civic_cases + case_events | repository/UoW dependent | owner UPDATE + event |
| case:mark_ready | CivicCaseCapability.transition | CivicCaseRepository.save | civic_cases + case_events | repository/UoW dependent | owner UPDATE + event |
| case:begin_submission | CivicCaseCapability.transition / SubmissionCapability | SubmissionCaseTransactionRepository | civic_cases + civic_case_submissions + case_events | atomic | owner + submission workflow |
| case:queue_submission | CivicCaseCapability.transition / SubmissionCapability | SubmissionCaseTransactionRepository | civic_cases + civic_case_submissions + case_events | atomic | owner + submission workflow |
| case:submit | SubmissionCapability + Case transition | SubmissionCaseTransactionRepository | civic_cases + civic_case_submissions + case_events | atomic | owner + consent + approval + idempotency |
| case:acknowledge | SubmissionCapability / Case transition | SubmissionCaseTransactionRepository or repository path | civic_cases + submissions + events | atomic where submission path | owner + evidence/ack boundary |
| case:verify_resolution | CivicCaseCapability.transition | CivicCaseRepository.save | civic_cases + case_events | repository/UoW dependent | owner UPDATE + event |
| case:reopen_resolution | CivicCaseCapability.transition | CivicCaseRepository.save | civic_cases + case_events | repository/UoW dependent | owner UPDATE + event |
| evidence:register | EvidenceCapability.register | EvidenceRepository.save | evidence persistence surface | repository-defined | GAP: evidence table not in candidate RLS set |
| evidence:attach | EvidenceCapability.attach → CivicCaseCapability.add_evidence | CivicCaseRepository.save | civic_cases + case_events + evidence refs | repository/UoW dependent | owner Case + evidence reference integrity |
| evidence:read | EvidenceCapability.get_for_case | EvidenceRepository.get | evidence + Case refs | read | GAP: evidence table policy absent |
| case:consent | ConsentCapability.record_submission_consent → Case add_consent | ConsentRepository.save + CivicCaseRepository.save | civic_case_consents + civic_cases + events | NOT atomic across both in current path | subject RLS + Case owner; cross-store atomicity GAP |
| case:reconcile_submission | SubmissionReconciliationCapability | SubmissionCaseTransactionRepository.persist_mutation | submissions + cases + events | atomic | owner + reconciliation policy |
| document:read | DocumentReviewCapability | document repository/blob boundary | document subsystem | repository-defined | GAP: explicit RLS mapping absent |
| document:edit | DocumentReviewCapability | document repository/blob boundary | document subsystem + Case refs where applicable | repository-defined | GAP |
| edit | DocumentReviewCapability | document repository/blob boundary | document subsystem | repository-defined | GAP; legacy/general action must not be accepted without explicit capability mapping |
| sos:trigger | SOS capability | external side-effect boundary | SOS subsystem | workflow-dependent | GAP: not a Civic Case RLS operation |

## High-value findings

### P1 — Child-row RLS currently does not enforce the action that creates the child row

The candidate child policies primarily derive access from existence of the Case row. Because Case access is currently owner-only, this does not create an immediate cross-user read path, but it is still broader than the action contract for future delegated access.

**Decision:** keep candidate delegation disabled. Before enabling delegated mutation, child INSERT/UPDATE policies must encode the corresponding action boundary or use a trusted backend-only write role.

### P2 — Evidence persistence is outside the candidate RLS table set

The active Evidence capability persists EvidenceObject records, but the candidate RLS migration only protects Case evidence references. The underlying evidence persistence surface must be identified and secured before production RLS.

**Decision:** production RLS remains blocked.

### P3 — Consent recording is not one transaction with Case attachment in the current capability path

ConsentCapability saves the Consent and then attaches the consent reference to the Case. The existing atomic Submission+Case transaction does not automatically make these two writes atomic.

**Decision:** do not claim full consent/case atomicity. Add a provider-neutral atomic consent+case boundary if the invariant requires both writes to succeed or fail together.

### P4 — Document authorization is not yet mapped to PostgreSQL

The active Document Review capability exposes document:read, document:edit, and edit, but the candidate RLS policy does not cover the document subsystem.

**Decision:** explicit mapping required before production.

### P5 — Action registry is semantic, not proof

The registry establishes vocabulary, but it does not prove that the repository implementation enforces every property in the ActionSpec. Conformance tests must inspect the actual persistence boundary.

## Production gate additions

Production RLS remains blocked until:

- Evidence persistence has a defined authorization/database boundary.
- Consent + Case attachment atomicity is either guaranteed by a transaction or explicitly documented as intentionally non-atomic with recovery semantics.
- Document read/edit authorization is mapped to its persistence boundary.
- Child-row write policies cannot exceed their parent capability boundary.
- All registered high-risk actions have real PostgreSQL negative tests.
