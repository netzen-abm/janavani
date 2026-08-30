# JANAVANI — CAPABILITY × ACCESS-SURFACE MATRIX

**Status:** CANONICAL EXECUTION MATRIX — v1.0  
**Date:** 30 August 2026  
**Purpose:** Map the complete Janavani capability inventory to the WebApp, Telegram Bot, and Telegram Mini App without allowing any access surface to become the owner of shared business logic.

## Governing rules

1. **Optional means optional for the citizen, not optional for the ecosystem.**
2. Every approved capability is shared infrastructure first.
3. WebApp, Telegram Bot, and Telegram Mini App are access surfaces; they do not own domain state or business logic.
4. AI is optional for the user, but AI capability infrastructure remains part of Janavani.
5. A capability may be `planned`, `partial`, `verified`, or `unavailable` on a surface without changing the capability's ecosystem scope.
6. Provider implementations remain behind stable capability contracts.
7. Personal Case/Evidence data remains local-first and must not be sent to AI merely because AI is available.
8. No surface may claim submission, delivery, or external action without confirmed acknowledgement.

## Status vocabulary

- **PLATFORM:** capability is part of Janavani's canonical ecosystem.
- **SURFACE:** whether the surface is an intended consumer.
- **IMPLEMENTATION:** current implementation state on that surface; this matrix is not a claim of runtime verification unless marked `VERIFIED`.

## Matrix

| Capability | Ecosystem | WebApp | Telegram Bot | Telegram Mini App | Notes / canonical owner |
|---|---|---|---|---|---|
| `JNV-CIVIC-COMPLAINT` | PLATFORM | Planned/Active | Planned | Planned | Shared civic workflow; Case owns state |
| `JNV-CIVIC-GRIEVANCE` | PLATFORM | Planned | Planned | Planned | Shared grievance workflow |
| `JNV-CIVIC-RTI` | PLATFORM | Planned | Planned | Planned | Authority + Document + tracking composition |
| `JNV-CIVIC-PETITION` | PLATFORM | Planned | Planned | Planned | Purpose-bound document/action workflow |
| `JNV-CIVIC-OBJECTION` | PLATFORM | Planned | Planned | Planned | Source-backed objection workflow |
| `JNV-CIVIC-APPEAL` | PLATFORM | Planned | Planned | Planned | Uses case history and authoritative procedure |
| `JNV-GOV-OFFICE-SEARCH` | PLATFORM | Planned | Planned | Planned | Authority capability; no personal identity required for search |
| `JNV-GOV-OFFICER-SEARCH` | PLATFORM | Planned | Planned | Planned | Public/official role information only; privacy constrained |
| `JNV-GOV-SCHEME-SEARCH` | PLATFORM | Planned | Planned | Planned | Source-grounded government information |
| `JNV-GOV-SCHEME-ELIGIBILITY` | PLATFORM | Planned | Planned | Planned | Assistance only; never represented as official determination |
| `JNV-GOV-ALERT-PUBLIC` | PLATFORM | Planned | Planned | Planned | Authenticated official source; AI never becomes authority |
| `JNV-ACCOUNTABILITY-OFFICE-REVIEW` | PLATFORM | Planned | Planned | Planned | Moderation, provenance and allegation/fact distinction |
| `JNV-ACCOUNTABILITY-OFFICER-REVIEW` | PLATFORM | Planned | Planned | Planned | Focus on official conduct/service |
| `JNV-ACCOUNTABILITY-REPRESENTATIVE-REVIEW` | PLATFORM | Planned | Planned | Planned | Public records + clearly labelled citizen experience |
| `JNV-ACCOUNTABILITY-GOV-PERFORMANCE` | PLATFORM | Planned | Planned | Planned | Source-linked datasets and methodology |
| `JNV-ACCOUNTABILITY-TRANSFER-CONCERN` | PLATFORM | Planned | Planned | Planned | Evidence-based concern; no presumption of wrongdoing |
| `JNV-ACCOUNTABILITY-MISBEHAVIOUR` | PLATFORM | Planned | Planned | Planned | Allegation remains an allegation pending evidence |
| `JNV-ACCOUNTABILITY-CORRUPTION` | PLATFORM | Planned | Planned | Planned | High-risk handling; secure reporting path |
| `JNV-DOC-GENERATE` | PLATFORM | Planned | Planned | Planned | Shared document capability; PDF/DOCX target |
| `JNV-DOC-ADDRESS-CORRECTION` | PLATFORM | Planned | Planned | Planned | Candidate correction + verification workflow |
| `JNV-DOC-EXPORT` | PLATFORM | Planned | Planned | Planned | Approved draft only |
| `JNV-EVIDENCE-CAPTURE` | PLATFORM | Planned | Planned | Planned | Local-first capture; attachments never owned by a channel |
| `JNV-EVIDENCE-PROVENANCE` | PLATFORM | Planned | Planned | Planned | Metadata/provenance capability |
| `JNV-EVIDENCE-BLOCKCHAIN-ANCHOR` | PLATFORM | Planned | Planned | Planned | Optional provider; normal operation must survive outage |
| `JNV-EVIDENCE-ARCHIVE` | PLATFORM | Planned | Planned | Planned | Retention policy + lawful deletion exceptions |
| `JNV-WB-SUBMIT` | PLATFORM | Planned | Planned | Planned | High-risk secure workflow; strict reviewer permissions |
| Case | PLATFORM | Active | Planned | Planned | Canonical shared domain object |
| Evidence | PLATFORM | Active | Planned | Planned | Shared evidence model |
| Provenance | PLATFORM | Active | Planned | Planned | Shared metadata/audit trail |
| Authority | PLATFORM | Active | Planned | Planned | Provider-neutral authority directory |
| Document | PLATFORM | In progress | Planned | Planned | Provider-neutral composition/rendering |
| Submission | PLATFORM | Planned | Planned | Planned | Explicit user approval + confirmed acknowledgement |
| Tracking | PLATFORM | Planned | Planned | Planned | Shared case timeline and follow-up |
| Identity | PLATFORM | Planned | Planned | Planned | User-controlled; channel identity must not become platform identity by default |
| Consent | PLATFORM | Planned | Planned | Planned | Cross-capability privacy/processing control |
| Privacy/Safety | PLATFORM | Active | Planned | Planned | Control plane across all surfaces |
| Local Vault | PLATFORM | Active | Planned | Planned | Web Crypto + IndexedDB target; mobile-native implementations later |
| AI | PLATFORM | In progress | Planned | Planned | Provider-neutral; user may choose AI or deterministic path |
| RAG | PLATFORM | Planned | Planned | Planned | Source-grounded intelligence; provenance required |
| Agentic AI | PLATFORM | Planned | Planned | Planned | Scoped tools, permissions, confirmation and audit |
| Notifications | PLATFORM | Planned | Planned | Planned | Channel-neutral notification capability |
| Search/Knowledge | PLATFORM | Planned | Planned | Planned | Shared source/knowledge infrastructure |
| Storage | PLATFORM | In progress | Planned | Planned | Provider-neutral storage boundary |
| Transport | PLATFORM | In progress | Planned | Planned | Internet and future alternative transports via adapters |
| Decentralized Infrastructure | PLATFORM | Architecture | Planned | Planned | Freenet/Nostr/Nym/Reticulum/blockchain etc. as providers/adapters |
| Emergency Safety Layer | PLATFORM | Planned | Planned | Planned | Separate from ordinary complaint workflow |

## Surface semantics

### WebApp

The WebApp is the first rich proving surface. It should expose the canonical civic-action workspace and consume shared contracts. It must not become the implementation owner of Case, Evidence, Authority, AI, Document, Submission or Tracking.

### Telegram Bot

The Bot is a complete Janavani access channel appropriate to Telegram's interaction model. It must not remain a complaint-only AI bot. Conversational interaction is an adapter into shared capabilities.

### Telegram Mini App

The Mini App is the rich Telegram access surface. It shares the same capability contracts, Case model, evidence model, authority model, document model, privacy policy and submission/tracking state as WebApp. It must not fork business logic from the Bot or WebApp.

## Capability continuity rule

A citizen may move between WebApp, Telegram Bot and Telegram Mini App without creating separate business concepts for the same civic action. Where identity/linking policy permits, the same Case and its authorized state should remain continuous.

The surfaces may differ in presentation and interaction, but the underlying capability contract remains stable.

## AI routing rule

For any capability marked `AI: Optional`:

```text
User request
  -> capability contract
  -> AI policy
      -> deterministic path
      -> local AI path
      -> approved remote AI path
      -> RAG path
      -> agentic path
  -> capability result
```

Remote AI processing requires the applicable privacy/consent gate. Encryption alone is not permission to transmit personal Case/Evidence data.

## Completion rule

A row is not `COMPLETE` merely because a UI exists. Completion requires:

- shared contract;
- implementation;
- privacy/safety enforcement;
- tests;
- provider/adapter boundary;
- surface integration;
- runtime verification;
- documentation;
- failure/degraded-path verification.

## Immediate execution order

1. Complete WebApp vertical slice: `Case -> Evidence -> Authority -> Document -> Review -> Submission -> Tracking`.
2. Make Telegram Bot consume the same shared capabilities rather than expanding Telegram-specific business logic.
3. Build Telegram Mini App as a rich consumer of the same contracts.
4. Verify cross-surface continuity and permissions.
5. Expand the same matrix to Android, iOS, WhatsApp, Messenger and DApp after the shared contracts are stable.
