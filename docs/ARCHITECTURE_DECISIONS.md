# JANAVANI — ARCHITECTURE DECISION INDEX

**Status:** ACTIVE — DECISION REGISTER
**Version:** 2.0
**Date:** 11 September 2026

This file records concise architectural decisions. Detailed rules belong in the canonical architecture documents; this file must not become a second architecture specification.

## ADR-001 — Workflow Engine

**Status:** ACCEPTED

Separate workflow execution from Telegram/interface code. Reusable workflows must be interface-neutral.

## ADR-002 — Responsibility-Based Repository Structure

**Status:** ACCEPTED

Organize code by responsibility and preserve clear ownership boundaries. Do not create parallel layers for cosmetic reasons.

## ADR-003 — Privacy First

**Status:** ACCEPTED

Privacy by Design and Privacy by Default are ecosystem invariants. Personal/sensitive data remains under user/device control by default.

## ADR-004 — Shared Document Composition

**Status:** ACCEPTED

Reuse document composition blocks across complaint, RTI, petition, representation, appeal and related civic documents. Document generation is separate from submission.

## ADR-005 — Complete Ecosystem, Not MVP Product Boundary

**Status:** ACCEPTED

Janavani is one complete citizen-governance ecosystem. Web, mobile, Telegram, messaging, DApp/Web3, AI, resilience and other implementations are construction surfaces/capabilities, not separate products or scope reductions.

## ADR-006 — Shared Infrastructure First

**Status:** ACCEPTED

Every reusable function, capability, workflow, service, skill, tool and provider integration is designed as shared infrastructure first. Interfaces consume it through contracts. Interface-specific business logic requires an explicit exception.

## ADR-007 — Optional Means User Choice

**Status:** ACCEPTED

A capability may be optional for the citizen while remaining part of the Janavani ecosystem. AI, Agentic AI, Web3, transport choices and cross-channel linking must not be silently forced. Safety/legal/device/network constraints must be explicit.

## ADR-008 — Provider Neutrality

**Status:** ACCEPTED

Databases, AI providers, messaging platforms, decentralized networks, government APIs and future technologies are adapters/providers. They do not define Janavani's domain model or become universal dependencies without explicit justification.

## ADR-009 — Rust Core, Incremental Migration

**Status:** ACCEPTED

Rust is the canonical long-term domain/core direction. Python remains appropriate at application/integration edges during migration. Do not perform a broad rewrite solely to change language; migrate bounded responsibilities behind stable contracts and verified behavioral parity.

## ADR-010 — Local-First Private Data

**Status:** ACCEPTED

Private Case/Evidence data is local-first where practical. No implicit remote fallback. Encryption is not permission to collect, and AI consent is not blanket permission to transmit personal data.

## ADR-011 — Canonical Case Across Surfaces

**Status:** ACCEPTED

Web, Telegram, Mini App, mobile and other access surfaces operate on one canonical Case/lifecycle model. A citizen moving between surfaces should continue the same civic matter rather than create interface-specific business state.

## ADR-012 — Document Generation Is Not Submission

**Status:** ACCEPTED

Generated documents are for citizen review, correction, print/download and submission guidance. Electronic submission is a separate capability with explicit destination, authorization, delivery and acknowledgement semantics.

## ADR-013 — Controlled Agentic AI

**Status:** ACCEPTED

Agentic AI uses scoped tools and policy. Consequential actions require appropriate authorization and user confirmation. Agent/provider failure must not remove deterministic paths where practical.

## ADR-014 — Evidence and Provenance Separation

**Status:** ACCEPTED

Evidence bytes, provenance metadata, analysis and civic action are separate concerns. Original evidence remains local by default. Provenance records should not become an attachment store.

## ADR-015 — Canonical Execution/Provenance Envelope

**Status:** DESIGN DIRECTION — IMPLEMENTATION NOT YET CLAIMED

Shared capability invocations should eventually use a provider-neutral execution context and operation/provenance records covering actor, capability, operation, resource, surface, provider, authorization/consent, data purpose/class, inputs, result, side effects, retry/idempotency and provenance. This is a future shared primitive, not yet a production implementation.

## ADR-016 — Archive Before Deletion

**Status:** ACCEPTED

Historical or superseded work is preserved before deletion. Removal requires replacement evidence, dependency/import checks, runtime verification where relevant, tests and documentation reconciliation.

## ADR-017 — Documentation Has an Authority Hierarchy

**Status:** ACCEPTED

`docs/DOCUMENTATION_INDEX.md` defines the documentation authority map. New Markdown files require a distinct responsibility; duplicates must be consolidated or archived after content review. Historical audits remain evidence and are not silently rewritten.

## Decision discipline

A new major architectural decision must:

1. identify the problem;
2. inspect existing documents and implementation;
3. state the decision and scope;
4. identify alternatives/rejected approaches where useful;
5. define consequences;
6. update affected canonical documents;
7. update the task/status register where execution changes.

**Do not use this register as a substitute for detailed architecture specifications.**
