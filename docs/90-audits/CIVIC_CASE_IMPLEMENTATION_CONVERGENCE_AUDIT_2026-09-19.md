# Civic Case Implementation Convergence Audit — 2026-09-19

**Status:** EVIDENCE / VERIFYING
**Scope:** Python domain/runtime, repository providers, capability composition, Rust parity, tests
**Rule:** Audit actual implementation before changing architecture.

## Executive finding

The repository already contains a substantial Civic Case vertical slice. The principal gap is **convergence and semantic parity**, not absence of a Civic Case implementation.

The inspected implementation establishes:

- a channel-neutral Python Civic Case aggregate;
- a canonical Python lifecycle transition matrix;
- provider-neutral Civic Case capability;
- evidence, consent, document review, submission and follow-up capabilities;
- external-channel discovery;
- explicit approval for consequential submission;
- in-memory and durable repository implementations;
- PostgreSQL/Supabase repository paths;
- a Rust janavani-core Civic Case implementation;
- contract and vertical-slice tests.

Therefore the next engineering objective should **not** be a new product subsystem. It should be to close the remaining semantic/runtime convergence gaps and prove the canonical path end-to-end.

## 1. Product-to-code mapping

| Product primitive | Current implementation evidence | Assessment |
|---|---|---|
| Civic Case | `src/core/civic_case.py`, `src/capabilities/civic_case.py` | Implemented |
| Case lifecycle | `src/core/case_lifecycle.py` | Implemented, but semantic gaps remain |
| Evidence reference | `src/capabilities/evidence.py` + case evidence refs | Implemented |
| Authority | authority capability/repository and case references | Implemented |
| Civic Action | `src/capabilities/civic_action_capability.py` | Implemented |
| Consent | `src/capabilities/consent.py` + case consent refs | Implemented |
| Authorization | capability authorization path | Implemented |
| Consequential approval | vertical-slice submission tests | Implemented |
| Submission | `src/capabilities/submission.py` | Implemented |
| External channel | `src/capabilities/external_channel.py` | Implemented |
| Submission reconciliation | `src/capabilities/submission_reconciliation.py` | Implemented |
| Follow-up | `src/capabilities/follow_up.py` | Implemented |
| Outcome | Case response/resolve/close semantics | Implemented at domain level |
| Durable case persistence | repository/provider implementations exist | Implemented in code; production activation remains separately gated |
| Cross-surface access | Web adapter and shared capability tests exist | Partially verified |
| Rust parity | `crates/janavani-core/src/civic_case.rs` | Exists; parity verification remains required |
| External-service orchestration contract | draft PR #197, not merged into main | Not canonical on main |

## 2. Strong architectural result

The current code already follows the intended dependency direction in the core path:

```
Surface
  ↓
Capability / vertical slice
  ↓
Domain aggregate
  ↓
Repository / provider contract
  ↓
Provider implementation
```

The vertical-slice tests also demonstrate that:

- case creation uses the shared Civic Case capability;
- evidence is registered and attached through capabilities;
- consent is explicit;
- document review occurs before submission;
- review and approval are separate steps;
- external channels are verified before use;
- submission requires explicit user approval;
- submission does not automatically equal acknowledgement;
- follow-up recommendation consumes the canonical case.

This is the right architectural direction.

## 3. Highest-value convergence gap: lifecycle semantics

The Python domain and lifecycle matrix are close, but not completely unified.

The lifecycle contract contains states including:

```
DRAFT → REVIEW → READY → SUBMITTING → QUEUED → SUBMITTED
→ ACKNOWLEDGED → FOLLOW_UP / IN_PROGRESS / RESPONDED / ESCALATED
→ RESOLVED → CLOSED → ARCHIVED
```

The domain aggregate contains these states, but the implementation deliberately does not expose every state mutation. In particular, `IN_PROGRESS` and `ARCHIVED` are represented in the graph but do not currently have full domain command semantics.

This is documented intentionally in `CASE_LIFECYCLE_SEMANTICS.md`. Therefore this is **not a bug to fix by adding arbitrary methods**.

The correct next step is to define authoritative evidence/source semantics for any new lifecycle mutation before exposing it.

## 4. Important state-model issue to resolve

The product-spine document introduced product-level states such as:

- `DISCOVERED`
- `SERVICE_IDENTIFIED`
- `SERVICE_VERIFIED`
- `READY_FOR_ACTION`
- `REVIEW_REQUIRED`
- `APPROVED`
- `EXTERNALLY_ACKNOWLEDGED`
- `UNDER_PROCESSING`
- `ACTION_REQUIRED`
- `PARTIALLY_RESOLVED`
- `REJECTED`
- `WITHDRAWN`
- `UNKNOWN`
- `FAILED`
- `EXPIRED`
- `REVOKED`

The existing domain model uses a different, narrower lifecycle vocabulary.

**Do not simply add all product-spine labels to `CaseStatus`.**

The product spine is a product abstraction; the domain status is an executable state machine. They must be reconciled through an explicit mapping/semantic contract.

This is the single most important architectural issue exposed by this audit.

## 5. Submission truth boundary

The current code correctly separates:

```
SUBMITTING
    ↓
QUEUED
    ↓
SUBMITTED
    ↓
ACKNOWLEDGED
```

and the tests explicitly verify that `SUBMITTED` does not mean confirmed delivery/acknowledgement.

This boundary should be preserved.

The same distinction must continue through any external-service integration:

- Janavani initiated an attempt;
- transport accepted/processed the attempt;
- external system acknowledged it;
- external system reported processing;
- external system supplied a response.

These are different facts.

## 6. Ownership/security observation

The inspected Civic Case capability performs an ownership check for the case creator before mutation/read operations.

This is useful, but it should not become the final authorization architecture by itself.

The repository already contains the canonical authorization/policy boundary. The long-term invariant should be:

```
Identity
  ↓
Authorization / Policy
  ↓
Capability
  ↓
Resource ownership / domain invariants
  ↓
Repository
```

Do not replace the authorization system with simple `created_by == principal_id` checks. Ownership is a resource invariant; authorization is the policy decision.

## 7. Repository convergence

The repository contains multiple Civic Case persistence implementations:

- provider-neutral repository;
- in-memory repository;
- PostgreSQL repository;
- Supabase repository;
- transaction/reconciliation helpers.

This is appropriate for provider independence, but the production activation boundary remains important.

The existence of a PostgreSQL/Supabase adapter does not prove:

- migration readiness;
- runtime selection correctness;
- RLS correctness;
- transaction behavior under failure;
- restart durability;
- deployment configuration;
- production activation.

Existing architecture documents already recognize this distinction.

Therefore no storage implementation should be deleted merely because another exists.

## 8. Rust parity

A Rust Civic Case implementation exists in `crates/janavani-core/src/civic_case.rs`, with Rust serialization tests.

This establishes that Rust is not merely a future idea; it is already part of the implementation surface.

However, the presence of both Python and Rust models creates a parity obligation.

At minimum, the following must converge:

- CaseType values;
- CaseStatus values;
- CaseEventType values;
- serialization values;
- transition semantics;
- consent requirements;
- acknowledgement semantics;
- event identity/idempotency behavior;
- canonical-field preservation.

The repository already contains serialization/conformance tooling. The next step should be to make parity evidence explicit rather than assume parity from similar source code.

## 9. Tests

The current tests provide strong evidence for the intended happy path:

```
create
 → evidence
 → consent
 → document preparation/review
 → review
 → approval
 → explicit user approval
 → verified external channel
 → submission
 → non-acknowledged submitted state
```

There are also lifecycle, repository, submission, reconciliation and vertical-slice tests.

The remaining highest-value tests are not more happy-path tests. They are **convergence/failure tests**, especially:

1. Python ↔ Rust contract parity.
2. Provider-selection parity.
3. PostgreSQL/Supabase transaction failure behavior.
4. authorization vs ownership boundary.
5. idempotent retry/reconciliation.
6. external acknowledgement truth.
7. stale/concurrent case version updates.
8. cross-surface invocation producing identical lifecycle semantics.

## 10. What should NOT be done next

Do not:

- create a second Civic Case implementation;
- add a universal government credential vault;
- add a generic browser/RPA subsystem;
- add all product-spine statuses directly to the domain enum;
- replace repositories merely for architectural cleanliness;
- migrate to PostgreSQL merely because an adapter exists;
- delete Python because Rust exists;
- delete Rust because Python exists;
- merge draft PR #197 automatically;
- create another generic "ecosystem core" abstraction without implementation evidence.

## 11. Recommended next engineering gate

The next implementation gate should be:

**Canonical Civic Case Contract Convergence Gate**

It should prove:

```
Product semantics
      ↓
Python domain
      ↓
Rust domain
      ↓
Capability layer
      ↓
Repository contract
      ↓
Provider implementation
      ↓
Web / Telegram / other adapters
      ↓
Submission / acknowledgement reconciliation
```

with identical externally meaningful semantics.

## 12. Immediate implementation recommendation

Before adding functionality, implement a **machine-checkable contract-parity/convergence test suite** around the already existing contracts.

The first bounded implementation should therefore target:

1. canonical enum/status/event parity;
2. canonical transition parity;
3. canonical serialization parity;
4. submission/acknowledgement semantic parity;
5. provider-neutral repository conformance;
6. idempotency/concurrency invariants.

This is a smaller and safer change than expanding the product surface, and it directly converts the architectural design into enforceable evidence.

## 13. Audit conclusion

**Civic Case is not missing.**

The repository is further along than a feature-level view suggests.

The major remaining risk is **semantic drift between multiple implementation generations/languages/providers**, not lack of functionality.

Therefore the correct sequence is:

```
Converge contracts
      ↓
Prove parity
      ↓
Prove provider behavior
      ↓
Prove cross-surface behavior
      ↓
Only then expand product capabilities
```
