# Repository Rules

## 1 — Responsibility boundaries
Organize code by responsibility and architectural boundary, not by arbitrary file or class size.

Split a module only when the separation creates an independent boundary of:
- change/release cadence;
- trust or authorization;
- persistence/transaction ownership;
- provider/external-system dependency;
- deployment/runtime isolation; or
- independent reuse by another capability or surface.

Keep tightly coupled responsibilities together when splitting them would weaken invariants, obscure transaction semantics, fragment a state machine, or create duplicated orchestration.

**Rule:** split when the boundary strengthens the architecture; preserve cohesion when it does not.

## 2 — One canonical owner
Every business capability has one canonical owner. Multiple surfaces may consume it, but may not create competing domain implementations.

## 3 — No duplicate implementations
Do not create a second implementation merely because another surface, provider, language, or generation exists. Reuse the canonical contract and adapter boundary.

## 4 — Adapters stay thin
No business/domain lifecycle logic inside Telegram, Web, Android, iOS, WhatsApp, Messenger, DApp, or other interface adapters.

## 5 — Domain independence
Domain code must not depend on Telegram, Web, mobile, messaging frameworks, databases, or specific external providers.

## 6 — Workflow/application separation
Reusable workflows and application orchestration coordinate capabilities and policies. They must not become persistence implementations.

## 7 — Storage ownership
Repositories and persistence adapters own database/provider mechanics. Transaction boundaries remain explicit and are not duplicated across capabilities.

## 8 — Documents own document generation
Document composition/export belongs behind the document capability/provider boundary. Submission transport does not own document generation.

## 9 — Trust and authorization are explicit
Authentication, identity, authorization, consent, provenance, and consequential-action gates are separate trust boundaries. Do not bypass them for convenience.

## 10 — Provider neutrality
Provider-specific code stays behind explicit contracts. Provider multiplicity is acceptable only when it represents a real deployment, persistence, or external-system boundary.

## 11 — Privacy before convenience
Do not centralize sensitive data merely because a capability can process it. Local-first and purpose-bound transmission remain the default design constraints.

## 12 — Security is part of every design decision
Every new boundary must state its authorization, failure, recovery, audit/provenance, and data-handling implications.

## 13 — Archive before deletion
Preserve historical value before removing code or documentation. Delete only after replacement, dependency, runtime, and historical-value evidence is established.

## 14 — Verification before promotion
A capability is not production-ready merely because its code exists. Require implementation, tests, runtime verification, security/privacy evidence, failure isolation, and deployment evidence before promotion.

## 15 — Shared ecosystem infrastructure
New ecosystem surfaces must consume shared contracts and infrastructure. A surface outage must not disable unrelated surfaces; an AI/provider outage must not disable deterministic capabilities where practical.
