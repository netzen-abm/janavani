# JANAVANI — FULL ECOSYSTEM CHARTER

**Status:** LOCKED — CURRENT STRATEGIC IDENTITY
**Version:** 2.0
**Date:** 23 August 2026
**Repository:** `netzen-abm/janavani`

## 1. PURPOSE

This document establishes the current identity, scope, architecture, and development direction of Janavani.

It supersedes any older documentation that frames Janavani primarily as an MVP, a Telegram bot, a complaint generator, or a single-interface application.

Those descriptions may remain useful as historical records of earlier development stages, but they are not the current strategic definition.

## 2. WHAT JANAVANI IS

Janavani is a **full citizen-governance ecosystem** designed to help citizens understand public problems, access verified government information, prepare and execute lawful civic action, communicate with public institutions, track outcomes, contribute evidence and knowledge, and participate in transparent public accountability.

Janavani is not defined by a single interface, technology, database, AI model, or deployment.

The durable product is the shared capability platform and the citizen-governance system built around it.

## 3. THE CURRENT STRATEGIC OBJECTIVE

We are building the ecosystem itself.

We are **not building an MVP as the product objective**.

Existing working functionality is treated as an implementation foundation and verification baseline. It is not a ceiling on scope.

The engineering strategy is therefore:

```text
LOCK THE ECOSYSTEM ARCHITECTURE
        ↓
CONVERGE DOCUMENTATION
        ↓
CONVERGE SHARED PLATFORM CAPABILITIES
        ↓
BUILD AND VERIFY REAL CAPABILITIES
        ↓
EXPOSE THEM THROUGH INDEPENDENT INTERFACES
        ↓
HARDEN SECURITY / PRIVACY / OPERATIONS
        ↓
EXPAND THE ECOSYSTEM
```

## 4. ECOSYSTEM SURFACE

Janavani is intended to provide independent access through multiple surfaces:

- Dynamic Web application
- Android application
- iOS application
- Telegram Bot
- Telegram Mini App
- WhatsApp integration
- Messenger integration
- Public/partner API
- DApp / Web3 interface where justified
- Decentralized-capable transports and services
- Future interfaces that conform to the platform contracts

The list is a product-scope map, not a claim that every surface is already production-ready.

## 5. ONE PLATFORM — MANY INTERFACES

The canonical model is:

```text
                       JANAVANI PLATFORM
                              │
       ┌──────────────────────┼──────────────────────┐
       │                      │                      │
   CAPABILITIES            DATA / TRUST          TRANSPORT
       │                      │                      │
       └──────────────────────┼──────────────────────┘
                              │
                 ┌────────────┼────────────┐
                 │            │            │
                Web        Mobile       Messaging
                 │          Android      Telegram
                 │          iOS          WhatsApp
                 │                       Messenger
                 │
                 └──── DApp / Web3 / API ────┘
```

Every interface consumes shared Janavani capabilities.

No interface owns core business logic.

No interface is a required dependency of another interface.

## 6. CAPABILITY-FIRST ARCHITECTURE

The platform is organized around reusable capabilities rather than around channels.

Core capability families include:

- Citizen identity, consent, and user control
- Issue understanding and classification
- Government office and authority intelligence
- Civic documents and document composition
- Evidence capture, organization, and provenance
- Submission and delivery
- Case/complaint lifecycle and tracking
- Follow-up and escalation
- RTI and civic-legal workflows
- Government schemes and benefits intelligence
- Public policy / law / notification intelligence
- Citizen feedback and corrections
- Office and public-service accountability
- Public representative information
- Government performance and financial-transparency intelligence
- Expert / volunteer / NGO / institution participation
- Emergency / SOS capability
- Multilingual and accessibility services
- AI / RAG / SLM / LLM assistance
- Analytics and public-learning systems

Capabilities may be exposed through any compatible interface.

## 7. AI IS OPTIONAL INFRASTRUCTURE

AI is a platform capability, not the identity of Janavani.

AI must be replaceable and independently operable.

The platform must remain functional for defined workflows when an AI provider is unavailable.

AI outputs must preserve the distinction between:

- Citizen-provided information
- Verified authoritative information
- System-derived information
- AI-assisted suggestions
- Unverified information

AI must not fabricate facts, authorities, legal provisions, evidence, or government actions.

## 8. PRIVACY AND SECURITY ARE SYSTEM INVARIANTS

Privacy by Design and Privacy by Default apply across the entire ecosystem.

Security is not an interface feature.

The architecture must support:

- Minimum necessary data collection
- Consent and purpose control
- Identity minimization
- Data separation where appropriate
- Secure evidence handling
- Retention and deletion controls
- Access control
- Auditability
- Threat modelling
- Abuse prevention
- Failure isolation

Privacy and security requirements must be testable, not merely documented.

## 9. DYNAMIC WEB

The Web is a major product surface, not a temporary MVP shell.

The dynamic website will progressively provide:

- Citizen workflows
- Account and consent controls
- Government information discovery
- Document creation
- Evidence workflows
- Tracking
- Feedback
- Governance intelligence
- Public dashboards where appropriate
- Multilingual and accessibility features
- Integration with the same platform used by other interfaces

## 10. MOBILE

Android and iOS are first-class interfaces.

They must consume the shared platform and must not depend on Telegram, WhatsApp, Web, or another interface for core functionality.

The mobile architecture should support appropriate offline/low-bandwidth operation where required by the capability and transport contracts.

## 11. TELEGRAM

Telegram remains an important operational interface because it already contains a working citizen workflow.

It is an interface, not the platform.

The Telegram Bot and future Telegram Mini App must consume shared capabilities.

The working Telegram flow should be protected from unnecessary refactoring while shared-platform convergence continues.

## 12. WHATSAPP AND MESSENGER

WhatsApp and Messenger are independent access channels.

They must connect to Janavani capabilities through adapters/integration boundaries.

Neither channel may become the owner of workflows, data, or business logic.

## 13. DAPP / WEB3 / DECENTRALIZED CAPABILITY

Web3 and decentralized technology are part of the ecosystem scope where they provide a real architectural or citizen benefit.

Potential roles include:

- Decentralized identity
- Citizen-controlled credentials
- Verifiable records
- Decentralized evidence/provenance
- Censorship-resilient communication
- Community-operated infrastructure
- Alternative storage/transport
- DApp access to selected Janavani capabilities

These technologies must be capability-driven rather than technology-driven.

Blockchain, IPFS, Nostr, Nym, Reticulum, mesh, satellite, or other decentralized components must not be treated as mandatory dependencies for capabilities that do not require them.

## 14. SOS / RESILIENT COMMUNICATION

Emergency capability is part of the ecosystem architecture.

The architecture may support Internet, local, mesh, gateway, and satellite transports according to capability requirements and regulatory/technical feasibility.

Emergency functions must prioritize resilience, privacy, integrity, delivery state, and failure handling.

## 15. CITIZEN-GOVERNMENT LIFECYCLE

The ecosystem is designed around the full lifecycle, not document generation alone:

```text
Citizen Reality
      ↓
Understand
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

## 16. GOVERNANCE INTELLIGENCE

Janavani may progressively connect public information across:

- Government departments
- Local governments
- Offices and services
- Schemes and benefits
- Laws, rules, bills, notifications, and policies
- Public budgets and expenditure
- Projects and implementation
- Elected representatives
- Citizen experience
- Accountability and outcome data

Public claims must use provenance and distinguish verified information from citizen reports, analysis, and AI assistance.

## 17. STATUS LANGUAGE

Every capability and document must distinguish among:

`VISION`
`DESIGNED`
`IMPLEMENTED`
`FUNCTIONAL`
`TESTED`
`SECURITY-VERIFIED`
`PRIVACY-VERIFIED`
`PRODUCTION-READY`
`ARCHIVED`

A capability is not considered complete merely because code, a prototype, or documentation exists.

## 18. DOCUMENTATION AUTHORITY

The documentation hierarchy is:

```text
JANAVANI ECOSYSTEM CHARTER
        ↓
NORTH STAR
        ↓
SOURCE OF TRUTH
        ↓
MASTER ARCHITECTURE
        ↓
PRODUCT LANDSCAPE
        ↓
ROADMAP
        ↓
CAPABILITY REGISTRY / CONTRACTS
        ↓
MASTER TASK CHECKLIST
        ↓
CODE / TESTS / DEPLOYMENT
```

Where documents conflict, the conflict must be explicitly reconciled. No silent interpretation is permitted.

## 19. ARCHIVE RULE

Historical MVP documents, obsolete architectural proposals, superseded roadmaps, and experimental plans may be archived.

Archive rather than delete when historical context has value.

Before archiving:

1. Identify the replacement/current document.
2. Migrate active references.
3. Verify no active dependency.
4. Preserve the historical content in an archive path.
5. Record the reason and date.

Deletion is a later, separately verified action and is not the default.

## 20. DEVELOPMENT RULE

Do not repeatedly rediscover the architecture.

Before a new engineering task:

1. Check the Ecosystem Charter.
2. Check the North Star.
3. Check Source of Truth.
4. Check the Master Architecture.
5. Check the capability registry.
6. Check the Master Task Checklist and subtasks.
7. Inspect the actual GitHub implementation.
8. Make the smallest justified change.
9. Test and verify.
10. Update documentation when the architecture or capability state changes.

## 21. FINAL DEFINITION

**Janavani is a citizen-governance ecosystem: one shared, privacy-first, capability-oriented platform exposed through independent web, mobile, messaging, API, and decentralized-capable interfaces.**

The objective is not to finish an MVP.

The objective is to build, verify, and progressively operationalize the full ecosystem.
