# Janavani Verification Model

**Status:** Authoritative verification policy  
**Date:** 2026-08-26

## Principle

Janavani must never obtain a green status by hiding a failure, weakening a meaningful assertion, skipping an applicable check, or presenting simulated evidence as real capability evidence.

## Evidence classes

### 1. Contract verification

Verifies interfaces, schemas, invariants, state transitions and safety rules in isolation.

### 2. Component/integration verification

Verifies that real Janavani components interact correctly across an explicitly defined boundary.

### 3. Provider diagnostic

Verifies that an external provider is reachable or configured at the time of the diagnostic. Provider diagnostics are not substitutes for deterministic contract tests.

### 4. End-to-end verification

Verifies a complete user-visible workflow across the intended runtime boundaries.

### 5. Deployment/runtime verification

Verifies that the declared production target actually starts and exposes the expected behavior.

## Mock policy

Mocks, fakes and emulators are allowed when they isolate a boundary or make deterministic testing possible. Their scope must be explicit.

A mock may prove:

- request construction;
- adapter behavior;
- error handling;
- contract compliance;
- deterministic business logic.

A mock cannot prove:

- a real provider is reachable;
- real credentials work;
- a production deployment works;
- a real messaging channel delivered a message;
- a real blockchain transaction was confirmed;
- an external authority accepted a submission.

## Failure reporting

Every applicable verification should produce a truthful state:

`PASS`, `FAIL`, `BLOCKED`, or `NOT APPLICABLE`.

`NOT APPLICABLE` must have a documented reason. It must never be used simply to avoid an expected failure.

## Capability status

Use the following repository-level status terms:

- **VERIFIED** — evidence is sufficient for the specific claim.
- **PARTIALLY VERIFIED** — material evidence exists but coverage is incomplete.
- **CONFIGURED** — implementation/configuration exists but runtime evidence is incomplete.
- **UNVERIFIED** — insufficient evidence.
- **FAILED** — relevant verification currently fails.
- **BLOCKED** — verification is prevented by a prerequisite failure.

## Release-gate rule

A release or milestone may only claim completion when its required evidence classes have passed. Passing unit tests alone does not establish production readiness.

## Failure-isolation rule

Verification must also test independence. A failure in one optional/user-selected capability must not automatically cause unrelated capabilities or access surfaces to report success, failure, or availability incorrectly.

Examples:

- AI unavailable → basic civic workflows remain truthful and usable where their dependencies permit.
- Telegram unavailable → Android remains independently operable.
- Storage provider unavailable → the system exposes a truthful storage failure/degraded state rather than fabricating persistence.
- Authority unresolved → the system does not silently choose an authority.
- Delivery uncertain → the system does not claim confirmed delivery.

## Documentation synchronization

Any newly implemented capability must update the appropriate authoritative documentation in the same change set. The documentation must state what is implemented, what is verified, what remains unverified, and which dependencies are optional from the user's perspective.
