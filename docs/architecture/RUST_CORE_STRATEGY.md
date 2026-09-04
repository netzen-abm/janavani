# Janavani Rust Core Strategy

**Status:** Adopted architectural direction  
**Date:** 2026-09-04

## Decision

Janavani will evolve toward a **Rust canonical domain/runtime core** while remaining polyglot at the application and integration edges.

Rust is the authoritative implementation target for shared domain truth; Python and other languages remain valid for adapters, AI/RAG experimentation, legacy migration, and channel-specific integration where they provide better delivery velocity.

## Why

Janavani is a long-lived civic infrastructure system with shared contracts for CivicCase lifecycle, evidence, authority resolution, consent, identity, documents, submission, policy, provenance, and auditability. These domains benefit from strong invariants, explicit error handling, predictable concurrency, and reusable WebAssembly-compatible components.

## Existing repository evidence

The repository already contains a Rust/Dioxus client under `src/web_dioxus`, and the canonical test orchestrator runs its Rust suite when that package is present. Historical `janavani_v2` and `janavani_v3` trees also contain Rust/Dioxus application structures. These generations are treated as migration evidence, not as new canonical application roots.

## Target architecture

```text
                    JANAVANI ECOSYSTEM
                           |
                  Canonical Domain Contracts
                           |
                    Rust Domain Kernel
                           |
          +----------------+----------------+
          |                |                |
       Python          Rust/WASM         Other
       adapters         clients         adapters
          |                |                |
       Telegram       Web / clients    external systems
       WhatsApp
       AI / RAG
```

## Core ownership

The future Rust kernel should own canonical domain behavior for:

- CivicCase and lifecycle transitions
- CaseEvent and event invariants
- Evidence metadata/provenance contracts
- Authority and destination contracts
- Consent and authorization invariants
- Document artifact semantics
- Submission state semantics
- Identity/policy primitives where appropriate

Persistence providers remain adapters. Telegram, Web, WhatsApp, AI, and other surfaces remain adapters. No access surface may create a competing lifecycle or domain model.

## Migration rule

**Do not rewrite the working Python system wholesale.**

Migration proceeds in vertical slices:

1. Freeze and test the language-neutral contract.
2. Implement the same contract in Rust as a reference/canonical kernel.
3. Add contract-equivalence tests between implementations where useful.
4. Move one capability at a time behind an adapter boundary.
5. Remove Python ownership only after runtime and migration evidence exists.

## Rust generation policy

Do **not** create another `janavani_v4` application tree. Existing Rust/Dioxus generations must be audited and either reused, consolidated, or archived under the repository's archive-first rule.

The canonical Rust core should live in a stable shared crate boundary rather than another generation-specific application directory.

## Non-goals

This decision does not require:

- an immediate Python rewrite;
- replacing PostgreSQL/Supabase providers;
- replacing Telegram or other adapters;
- forcing AI/RAG implementation into Rust;
- activating decentralized protocols merely because Rust supports them;
- changing production runtime behavior before contract and migration tests are green.

## Immediate sequence

1. Complete CivicCase lifecycle convergence in the current Python domain without changing semantics accidentally.
2. Establish the Rust canonical domain crate from the validated contract.
3. Implement lifecycle first and prove contract equivalence.
4. Extend the kernel capability-by-capability: events, evidence, authority, consent, documents, submission.
5. Migrate access surfaces only after stable capability boundaries exist.
