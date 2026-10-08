# Janavani Engineering Cycle Reset — 2026-10-08

## Decision

The next engineering cycle is a **proof cycle**, not an abstraction/construction cycle.

The canonical architecture is frozen at the current responsibility boundaries. No new universal orchestration layer, capability facade, provider abstraction, or surface-specific business implementation should be introduced unless a concrete failure demonstrates an independent boundary of change, trust, persistence, provider dependency, or reuse.

## Repository hygiene

Live GitHub verification on 2026-10-08 found exactly nine active branches:

1. main
2. integration/canonical-platform
3. audit/postgres-provider-production-gates
4. chore/ecosystem-shared-capability-infrastructure
5. feat/canonical-capability-execution-envelope
6. feat/canonical-case-kernel
7. feat/canonical-civic-action-vertical-slice
8. feat/canonical-sos-contract
9. feat/capability-scoped-consent-agent-enforcement

No tenth branch was created. No branch is deleted in this cycle because the repository already satisfies the exact-nine policy and several divergent branches contain historical work that must not be discarded without evidence.

### Branch disposition

- `feat/canonical-capability-execution-envelope`: 0 commits ahead of main; no merge required.
- `chore/ecosystem-shared-capability-infrastructure`: 0 commits ahead of main; no merge required.
- `integration/canonical-platform`: 13 commits ahead but 1,819 behind main; divergent. Wholesale merge is rejected.
- `feat/canonical-case-kernel`: 5 commits ahead but 1,836 behind; selectively extract only still-valid unique work.
- `feat/canonical-civic-action-vertical-slice`: 10 commits ahead but 1,486 behind; selectively evaluate unique changes.
- `feat/canonical-sos-contract`: 13 commits ahead but 1,124 behind; preserve as historical/feature work until SOS implementation is re-baselined.
- `feat/capability-scoped-consent-agent-enforcement`: 26 commits ahead but 1,821 behind; selectively re-evaluate authorization/consent work against current contracts.
- `audit/postgres-provider-production-gates`: 8 commits ahead but 1,622 behind; use as evidence source, not a wholesale merge target.

## PR #203

PR #203 (`integration/canonical-platform` → `main`) remains open and unmerged.

It is intentionally treated as a convergence review vehicle, not as a merge queue. Its required gates remain:

- real PostgreSQL cross-user authorization/RLS evidence;
- restart/outage/recovery evidence;
- backup/restore evidence;
- canonical Web/API runtime evidence;
- independent Telegram runtime evidence.

The PR is currently reported as non-mergeable. No blind merge is authorized.

## Architecture decision

The following boundaries remain canonical:

**Surface/Adapter → Capability Contract + Execution Context → Trust/Authorization/Consent → Domain Aggregate + Lifecycle → Content/Evidence → Submission/Delivery → Unit of Work/Transaction → Provider Adapter**

The split rule is:

> Split at boundaries of change, trust, persistence, provider dependency, independent reuse, independently testable lifecycle/state, or external transport/provider dependency. Preserve cohesion when splitting would duplicate orchestration or weaken invariants.

## Proof-cycle priorities

### Gate 1 — Canonical correctness

The previously identified Case/content → lifecycle → submission defects have been addressed in the current mainline implementation. The next action is verification, not another abstraction layer.

Required evidence:
- canonical Web vertical-slice gate;
- Web/Telegram shared-capability contract gate;
- canonical Python suite;
- Rust/Python lifecycle parity;
- transaction rollback and concurrency tests.

### Gate 2 — PostgreSQL production behavior

Required evidence:
- real PostgreSQL cross-user isolation;
- RLS enforcement for non-BYPASSRLS principals;
- authorization-denial tests;
- transaction-local principal context isolation;
- rollback/atomicity;
- restart durability;
- outage/recovery;
- backup/restore.

### Gate 3 — Runtime surface independence

Required evidence:
- canonical Web/API startup and health;
- independent Telegram startup;
- both consume the shared capability graph;
- failure of one surface does not require the other to remain running;
- provider configuration is independently verifiable.

### Gate 4 — Security/privacy

Verify:
- authorization and consent;
- session expiry/revocation;
- sensitive-content persistence boundary;
- log/telemetry redaction;
- document/artifact non-durability;
- provider and transport isolation.

## Explicit prohibition for this cycle

Do **not**:
- create another architecture generation;
- split cohesive Case/lifecycle orchestration merely because files are large;
- add a second Case capability;
- move provider SDKs into domain code;
- let surfaces mutate lifecycle directly;
- treat delivery acknowledgement as persistence success;
- merge divergent historical branches wholesale;
- claim production certification from static analysis or green CI alone.

## Exit criterion

The cycle succeeds when the existing architecture has runtime evidence across PostgreSQL, Web, and Telegram sufficient to move from **architecture convergence** to **production certification**.

Until then, the correct engineering action is to test, observe, record evidence, and fix only the smallest boundary-local defect.
