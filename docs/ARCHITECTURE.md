# JANAVANI — CANONICAL SYSTEM ARCHITECTURE

**Status:** LOCKED — CURRENT ARCHITECTURAL REFERENCE
**Version:** 2.0
**Date:** 23 August 2026
**Authority:** Subordinate to `JANAVANI_NORTH_STAR.md`, `JANAVANI_ECOSYSTEM_CHARTER.md`, and `SOURCE_OF_TRUTH.md`

## 1. Architectural identity

Janavani is one full citizen-governance ecosystem built from shared capabilities and experienced through independent interfaces.

It is **not an MVP architecture**. Individual workflows, releases, pilots, or implementation milestones are construction units inside the ecosystem.

## 2. Canonical architecture

```text
Citizen / External Actor
        ↓
Independent Interface / Integration
        ↓
API / Application Boundary
        ↓
Shared Janavani Capabilities
        ↓
Workflow + Domain + Services
        ↓
Data / Evidence / Trust / Storage
        ↓
External Government / Civic Systems
```

### Independent access surfaces

- Dynamic Web
- Android
- iOS
- Telegram Bot
- Telegram Mini App
- WhatsApp
- Messenger
- Public/partner APIs
- DApp / Web3 interfaces
- Resilient/offline/mesh/satellite-capable transports where justified

No interface owns shared business logic.

## 3. Core implementation layers

| Layer | Primary responsibility |
|---|---|
| `src/adapters/` | External interface and integration translation |
| `src/conversation/` | Conversational interaction and session flow |
| `src/workflow/` | Reusable workflow definitions/steps |
| `src/engine/` | Workflow/state orchestration |
| `src/domain/` | Core Janavani concepts and domain rules |
| `src/services/` | Application/business services and integrations |
| `src/documents/` | Document composition, standards and output |
| `src/storage/` | Persistence, repositories, transient cache and storage integrations |
| `src/models/` | Application/data models |
| `src/core/` | Shared configuration and platform-level services |
| `src/web/` | Web/API assembly and web-facing routes |

These mappings describe current repository responsibilities. They do not authorize duplicate implementations merely because multiple historical trees exist.

## 4. Workflow principle

A reusable citizen capability should follow the general pattern:

```text
Interface
  ↓
Request / Interaction
  ↓
Workflow
  ↓
Workflow Engine
  ↓
Domain + Services
  ↓
Evidence / Document / Delivery
  ↓
Tracking / Outcome
```

The same capability may be consumed by Web, mobile, messaging, API and other approved surfaces.

## 5. Current working foundation

The repository contains a working conversational/document foundation including issue intake, document selection, location/district handling, office search/fallback, identity, preview, document generation, tracking and feedback-related services.

The existence of this foundation does **not** define the product boundary.

## 6. Dynamic Web

Dynamic Web is a first-class product surface. It must consume shared platform capabilities rather than become a second implementation of core business logic.

It is independent of Telegram and must be capable of progressively exposing the wider ecosystem: citizen workflows, government intelligence, evidence, documents, tracking, feedback, accountability and public learning.

## 7. Mobile and messaging

Android and iOS are independent product surfaces.

Telegram Bot and Telegram Mini App are independent access surfaces.

WhatsApp and Messenger are independent adapters/integrations.

No channel may require another channel for ordinary operation.

## 8. API and DApp/Web3

APIs expose reusable capabilities through explicit contracts.

DApp/Web3, decentralized storage, verifiable credentials, provenance systems, Nostr/Nym/Reticulum and related technologies are optional architectural tools. Adoption requires a demonstrated capability, privacy, security, resilience or governance justification.

No decentralized component becomes a universal dependency merely because it exists in the repository.

## 9. AI architecture

AI is replaceable infrastructure and a purpose-bound capability.

```text
Citizen / Source Data
        ↓
Structured Context
        ↓
Retrieval / Classification / Assistance
        ↓
Source + Confidence + Provenance
        ↓
Human or deterministic validation where required
        ↓
Citizen-facing result
```

AI must not fabricate authorities, laws, evidence, government actions, delivery states or other consequential facts.

Non-AI fallback behaviour must exist where a capability is required to remain operational without AI.

## 10. Data, storage and provenance

Storage ownership is governed by `docs/STORAGE_OWNERSHIP_MAP_2026-08-23.md` and the canonical data contracts.

The architecture distinguishes:

- Persistent civic records
- Government/reference data
- Evidence
- User-controlled/private data
- Transient workflow state
- Cache/metrics data
- Historical/archive material

No storage technology is automatically the universal source of truth. Actual ownership and runtime usage must be verified before migration or deletion.

## 11. Privacy and security

Privacy by Design, Privacy by Default, data minimisation, consent, access control, evidence protection, retention discipline, auditability, threat modelling, abuse prevention and secure recovery are ecosystem invariants.

Information classes must remain distinguishable: citizen-provided, authoritative, system-derived, expert-reviewed, AI-generated and unverified.

## 12. Resilience and emergency capability

SOS and resilient transport have stronger requirements than ordinary workflows: explicit delivery states, retry semantics, integrity, replay protection, privacy, abuse controls and failure handling.

Internet, local, mesh, satellite-capable and other transports are adapters. A failed transport must never be represented as successful delivery.

## 13. Repository evolution rule

Before changing or removing implementation:

1. Check the canonical documentation hierarchy.
2. Check the Master Task Checklist and current status register.
3. Inspect actual imports/references and tests.
4. Determine runtime ownership.
5. Identify replacement implementation where applicable.
6. Make the smallest justified change.
7. Test and verify.
8. Update evidence and affected documentation.
9. Archive superseded documentation rather than allowing it to compete with current direction.

## 14. Completion discipline

A capability progresses through:

`VISION → DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → PRODUCTION-READY`

Documentation or source-code presence alone is not evidence of functional completion.

## 15. Architectural decision rule

The question is not whether a technology is sophisticated. The question is whether it advances a verified citizen capability while preserving independence, privacy, security, resilience and maintainability.

## 16. Canonical conclusion

**Janavani is a capability-first citizen-governance platform with many independent interfaces, not a collection of interface-specific applications. The ecosystem is the destination; individual releases and working flows are construction steps.**
