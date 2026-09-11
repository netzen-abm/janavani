# JANAVANI — DEVELOPER GUIDE

**Status:** ACTIVE — DEVELOPMENT ENTRY GUIDE
**Version:** 2.0
**Date:** 11 September 2026

## 1. Read first

Before changing code, read:

1. `docs/DOCUMENTATION_INDEX.md`
2. `docs/JANAVANI_NORTH_STAR.md`
3. `docs/JANAVANI_ECOSYSTEM_CHARTER.md`
4. `docs/SOURCE_OF_TRUTH.md`
5. `docs/JANAVANI_MASTER_ARCHITECTURE.md`
6. `docs/ARCHITECTURE.md`
7. `docs/ARCHITECTURE_PRINCIPLES.md`
8. `docs/PROJECT_MAP.md`
9. `ROADMAP.md`
10. `docs/MASTER_TASK_CHECKLIST.md`
11. Latest status register
12. Relevant capability/data contracts and evidence

For concise orientation, also read `docs/AI_HUMAN_DEVELOPER_CONTEXT.md`.

## 2. Core engineering rule

**Build shared infrastructure first. Interfaces are consumers. Providers are adapters.**

Before adding a feature, ask:

- Does the capability already exist?
- Where is its canonical owner?
- Can another interface reuse it?
- What are its data, consent, authorization, provenance and failure requirements?
- Is this replacing an existing generation or creating duplication?

If unclear, update the project map or create an ADR before multiplying code.

## 3. User choice

Optional means optional for the citizen, not optional for the ecosystem.

AI, Agentic AI, Web3, messaging, resilient transports and other optional capabilities remain ecosystem capabilities where in scope. The citizen chooses whether to invoke them, subject to explicit constraints.

## 4. Privacy and trust

Personal and sensitive data remains under user/device control by default. Do not create central collection merely because a capability could process the data.

Evidence originals remain local unless an explicitly authorised operation requires transmission.

Never treat encryption as permission to collect. Never treat AI consent as blanket data-sharing consent.

## 5. Canonical layering

```text
Interface / Adapter
        ↓
API / Application Boundary
        ↓
Shared Capability
        ↓
Workflow + Domain + Services
        ↓
Data / Trust / Provenance
        ↓
Provider / External System
```

Do not put shared business logic in Telegram, Web, Android, iOS, WhatsApp, Messenger or DApp code.

## 6. Case lifecycle

```text
Problem → Understand → Evidence → Jurisdiction → Authority
→ Action → Document → Review → Approval → Submission
→ Acknowledgement → Tracking → Follow-up/Escalation → Outcome
```

A Case is shared across access surfaces. Do not create interface-specific civic lifecycles.

## 7. AI and Agentic AI

AI is a shared, purpose-bound and replaceable capability. Local Ollama and cloud providers are adapters, not the architecture.

AI output is analysis unless supported by identified evidence. Critical claims require source/provenance handling.

Agentic AI uses scoped tools. Consequential actions require policy, authorization and appropriate user confirmation. Agent failure must not remove deterministic paths where practical.

## 8. Rust and Python

Rust is the canonical long-term domain/core direction. Python remains appropriate at application and integration edges during controlled migration.

Do not perform a broad rewrite merely to change languages. Stabilize contracts, prove behavior, then migrate bounded responsibilities.

## 9. Repository locations

- `src/domain/` — core domain concepts/rules
- `src/workflow/` — reusable workflows
- `src/engine/` — orchestration/state execution
- `src/services/` — application/business services
- `src/documents/` — document composition/output
- `src/storage/` — repositories/persistence/storage adapters
- `src/adapters/` — external interface/integration translation
- `src/conversation/` — interaction/session/routing
- `src/web/` — Web/API assembly
- `tests/` — automated verification
- `docs/` — active architecture, product, governance, security, audit and evidence documentation
- `planning/` — active detailed contracts/specifications
- `archive/` — historical/superseded material

Do not add a new top-level directory or duplicate layer without justification.

## 10. Documentation before code multiplication

Search Markdown and source before creating a new file.

If an existing document owns the subject, update it instead of creating another competing document.

If a document is obsolete, archive it with historical value preserved. Update references after archival.

## 11. Completion discipline

A file or class is not a completed capability.

Use:

`VISION → DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → FAILURE-ISOLATED → PRODUCTION-READY`

Production claims require runtime and deployment evidence.

## 12. Git workflow

Before a commit:

1. inspect current branch/base;
2. inspect related code and documentation;
3. make the smallest justified change;
4. run applicable tests and architecture checks;
5. review the diff for duplication/security/privacy regressions;
6. update evidence/documentation;
7. commit with a descriptive message.

Archive before deletion. Delete only after dependency, replacement, runtime and historical-value evidence.

## 13. PR review checklist

Every significant PR should answer:

- What capability does this implement or converge?
- What is the canonical owner?
- Does it duplicate existing code?
- Which interfaces can consume it?
- What provider dependencies exist?
- What happens when they fail?
- What personal/sensitive data crosses a boundary?
- What consent/authorization is required?
- What provenance/audit is produced?
- What tests prove the behavior?
- What remains unverified?

## 14. Final rule

Every PR should leave Janavani **simpler, safer, more reusable, more verifiable and better documented**. If it makes the architecture more complicated, contain the complexity behind a justified contract or ADR.
