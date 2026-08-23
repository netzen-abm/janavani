# JANAVANI — ECOSYSTEM ENGINEERING CONSTITUTION

**Status:** ACTIVE / LOCKED ENGINEERING PRINCIPLES
**Version:** 2.0
**Date:** 23 August 2026

## 1. Purpose

This constitution governs engineering for the full Janavani ecosystem.

It replaces the former MVP Constitution. The MVP-era document is archived as historical context.

## 2. Ecosystem-first

Janavani is built as a full citizen-governance ecosystem. No engineering decision may redefine the project as a single-interface MVP.

## 3. Capability-first architecture

Business capabilities belong to the shared Janavani platform. Interfaces consume capabilities.

## 4. Interface independence

Web, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, API, DApp/Web3, and future interfaces must remain independently replaceable and must not own one another's business logic.

## 5. Separation of responsibilities

```text
Interface / Adapter
        ↓
Interaction / Workflow
        ↓
Domain / Services
        ↓
Document / Evidence / Delivery
        ↓
Repositories / Storage
```

No UI-specific business logic should leak into shared services. Builders/renderers must not become database or channel owners.

## 6. AI independence

AI is optional, replaceable infrastructure. Core workflows must have defined non-AI fallback behavior.

## 7. Data provenance

Citizen input, authoritative sources, verified structured data, system-derived information, and AI suggestions must remain distinguishable.

## 8. Privacy and security

Privacy by Design, Privacy by Default, data minimization, consent, access control, secure evidence handling, auditability, threat modelling, and abuse prevention are system invariants.

## 9. Decentralized/Web3 technology

Decentralized technology may be used when a capability requires or materially benefits from it. Technology must follow capability requirements rather than dictate them.

## 10. Documentation-first change

Architectural changes require documentation reconciliation before or with implementation. The Ecosystem Charter, North Star, Source of Truth, Master Architecture, Product Landscape, Roadmap, capability contracts, and Master Checklist form the active documentation chain.

## 11. Verification-first change

A capability is not complete because code exists. Completion requires appropriate implementation, tests, source/file verification, security/privacy review, and functional verification.

## 12. Archive-over-delete

Superseded designs and historical decisions should be archived when useful. Active documentation must not contain contradictory historical strategy.

## 13. No-guessing rule

Before changing code, inspect the actual GitHub implementation, imports, dependencies, tests, deployment references, and capability ownership. Never invent files, functions, or architecture.

## 14. Small verified changes

Prefer:

```text
inspect → change → test → verify → document → commit
```

Avoid broad restructuring without a demonstrated architectural need.

## 15. Master checklist control

Every major capability has a master task ID and explicit subtasks. Work must be tracked through `docs/MASTER_TASK_CHECKLIST.md` and its status/evidence records.

## 16. Final principle

**Build one coherent Janavani ecosystem, not a collection of interface-specific applications.**
