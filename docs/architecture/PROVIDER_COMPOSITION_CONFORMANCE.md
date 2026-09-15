# Provider Composition Conformance Contract

## Purpose

The shared provider composition boundary defines **which provider is selected** for each persisted domain. Repository adapters remain domain-specific implementations of provider-neutral contracts.

This document separates three concerns:

1. **Composition** — one shared provider plan for the access-surface runtime.
2. **Repository contract** — provider-neutral domain operations.
3. **Adapter conformance** — each concrete provider must satisfy the applicable repository contract and its domain invariants.

## Mandatory composition invariants

Every persisted domain declared by `PERSISTED_DOMAINS` must:

- have a deterministic provider entry in the shared composition;
- default safely to `memory` for development when no provider is configured;
- normalize provider identifiers before selection;
- reject unknown persisted domains;
- reject empty provider identifiers;
- remain immutable once composed; overrides create a new plan;
- avoid importing or instantiating database clients merely to construct the plan.

Decision-only capabilities such as Follow-Up and Escalation are not persistence domains and must not acquire storage requirements without a separate architectural decision.

## Adapter conformance rule

A provider adapter may be added only when its domain contract is already explicit. The adapter must preserve the same observable domain semantics as the memory implementation, including validation, lifecycle invariants, authorization-relevant state, idempotency/concurrency requirements, and transaction boundaries where the domain requires them.

Provider-specific APIs must not leak into `src/core` contracts or access surfaces.

## Current posture

- `memory` remains the safe development default.
- PostgreSQL adapters already exist for several canonical domains.
- Accountability Feedback and External Channel do not yet require PostgreSQL adapters merely for completeness.
- Production migration is not authorized by this contract.
- Legacy JSONL/CSV sources remain preserved and read-only until a separately evidenced migration plan exists.

## Testing

`tests/test_provider_composition_conformance.py` verifies the shared composition invariants. Domain-specific adapter tests remain responsible for adapter behavior; this test must not become a substitute for repository-contract tests.

## Future gate

Before selecting a durable provider for a new persisted domain:

1. define or verify the provider-neutral repository contract;
2. provide the memory/reference implementation and contract tests;
3. implement the bounded durable adapter;
4. run the same contract tests against the durable adapter;
5. verify schema, transaction, concurrency, privacy, authorization, and migration evidence before production selection.
