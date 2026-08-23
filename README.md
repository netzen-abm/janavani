# 🇮🇳 JANAVANI — CITIZEN-GOVERNANCE ECOSYSTEM

**Status:** ACTIVE — ECOSYSTEM BUILD
**Version:** 2.0
**Date:** 23 August 2026
**Repository:** `netzen-abm/janavani`

## What is Janavani?

Janavani is a **full citizen-governance ecosystem**: a privacy-first, capability-oriented platform through which citizens can understand public problems, access verified government information, prepare lawful civic action, communicate with public institutions, track outcomes, contribute evidence and knowledge, and participate in public accountability.

Janavani is **not an MVP project** and is not a Telegram bot project.

The existing Telegram workflow is an important working foundation. The product objective is the complete ecosystem.

## Ecosystem surfaces

Janavani is designed to provide independent access through:

- Dynamic Web application
- Android application
- iOS application
- Telegram Bot
- Telegram Mini App
- WhatsApp integration
- Messenger integration
- Public/partner APIs
- DApp / Web3 capabilities where justified
- Decentralized, mesh, and resilient transport capabilities where required
- Future compatible interfaces

All interfaces consume the shared Janavani platform. No interface owns core business logic and no interface should depend on another interface for normal operation.

## Core ecosystem lifecycle

```text
Citizen Reality
      ↓
Understanding
      ↓
Evidence / Context
      ↓
Correct Authority
      ↓
Lawful Civic Action
      ↓
Submission / Communication
      ↓
Government Response
      ↓
Tracking
      ↓
Follow-up / RTI / Escalation
      ↓
Outcome
      ↓
Feedback / Accountability
      ↓
Public Learning
```

## Platform architecture

```text
                         JANAVANI PLATFORM
                                │
        ┌───────────────────────┼───────────────────────┐
        │                       │                       │
   CAPABILITIES             DATA / TRUST            TRANSPORT
        │                       │                       │
        └───────────────────────┼───────────────────────┘
                                │
      ┌───────────────┬─────────┼─────────┬───────────────┐
      │               │         │         │               │
     Web           Android     iOS    Telegram         WhatsApp
      │               │         │      Mini App        Messenger
      └───────────────┴─────────┼─────────┴───────────────┘
                                │
                         API / DApp / Web3
```

## Major capability families

- Citizen identity, consent, and user control
- Issue understanding and classification
- Government office and authority intelligence
- Civic documents and document composition
- Evidence and provenance
- Submission, delivery, and tracking
- Follow-up, RTI, appeal, and escalation
- Government schemes and benefits intelligence
- Public policy, law, bill, and notification intelligence
- Citizen feedback and knowledge contribution
- Office, officer, representative, and service accountability
- Government performance and financial-transparency intelligence
- Expert, volunteer, NGO, and institution ecosystem
- Emergency / SOS capability
- Multilingual and accessibility services
- AI / RAG / SLM / LLM assistance
- Analytics and public-learning systems
- Decentralized / Web3 capabilities where they provide real value

## AI principle

AI is a **replaceable platform capability**, not Janavani's identity and not an unrestricted chatbot.

Janavani must distinguish citizen-provided information, verified authoritative information, system-derived information, AI-assisted suggestions, and unverified information.

AI must not fabricate facts, government authorities, legal provisions, evidence, or government actions.

## Privacy and security

Privacy by Design, Privacy by Default, minimum-data collection, consent, access control, evidence protection, auditability, threat modelling, and abuse prevention apply across the ecosystem.

## Documentation authority

Start with:

1. `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — current identity and ecosystem scope
2. `docs/JANAVANI_NORTH_STAR.md` — strategic destination and civic purpose
3. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules
4. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — system architecture
5. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — capability landscape
6. `ROADMAP.md` — ecosystem construction sequence
7. `docs/MASTER_TASK_CHECKLIST.md` — master tasks and subtasks
8. `docs/CAPABILITY_REGISTRY.md` — capability status and ownership
9. `planning/` — active engineering contracts and detailed specifications
10. `docs/` — audits, architecture decisions, deployment and engineering records

Historical or superseded material belongs under `archive/` and must not be treated as current direction.

## Development rule

```text
Ecosystem Charter
      ↓
North Star
      ↓
Source of Truth
      ↓
Master Architecture
      ↓
Capability Registry
      ↓
Master Checklist + subtasks
      ↓
Actual GitHub code/tests
      ↓
Small verified change
      ↓
Tests + review
      ↓
Documentation update
```

Do not repeat an audit that has already been completed. Use dated audit records and the master checklist to identify the next unresolved question.

## Current engineering phase

The present phase is **ecosystem foundation convergence**: eliminate contradictory MVP-era language, establish one coherent ecosystem identity, reconcile architecture and product documents, establish capability/data/permission/transport/security/test contracts, verify current implementations against the target architecture, and then build and integrate capabilities across independent interfaces.

This is not a freeze on the ecosystem. It is the foundation required to build it coherently.

## Repository principle

GitHub is the primary engineering workspace and source for current implementation state. Local editors may be used operationally, but architectural decisions, documentation, code changes, tests, and evidence must be reconciled against GitHub.

## License

See `LICENSE`.
