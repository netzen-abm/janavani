# JANAVANI — PRODUCT LANDSCAPE

**Status:** LOCKED — CURRENT PRODUCT LANDSCAPE
**Version:** 2.0
**Date:** 23 August 2026

## 1. PURPOSE

This document describes Janavani as a full product ecosystem: what capabilities exist, what is being built, and the intended system of interfaces and governance services.

It is not an MVP roadmap.

## 2. JANAVANI IN ONE SENTENCE

**Janavani is a privacy-first citizen-governance ecosystem that helps citizens move from lived public problems to informed action, institutional response, follow-up, accountability and public learning through one shared capability platform exposed across independent interfaces.**

## 3. PRODUCT SURFACES

First-class surfaces include:

- Dynamic Web
- Android
- iOS
- Telegram Bot
- Telegram Mini App
- WhatsApp
- Messenger
- API
- DApp / Web3
- Decentralized/resilient transport interfaces where justified

## 4. PRODUCT MODEL

```text
                    JANAVANI PLATFORM
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   CAPABILITIES        DATA / TRUST       TRANSPORT
        │                  │                  │
        └──────────────────┼──────────────────┘
                           │
        ┌──────────┬───────┼───────┬──────────┐
        ↓          ↓       ↓       ↓          ↓
       Web      Android   iOS   Messaging   DApp/API
```

## 5. CAPABILITY FAMILIES

### Citizen interaction

Conversation, guided workflows, forms, session/state, language, accessibility.

### Intelligence

Issue understanding, classification, department/authority identification, office intelligence, location intelligence, legal-information assistance, AI/RAG.

### Civic action

Complaint, grievance, RTI, representation, petition, objection, appeal, follow-up, escalation and other lawful civic workflows.

### Evidence

Photo, video, document, voice where appropriate, OCR, metadata, provenance, verification and review.

### Delivery and lifecycle

Document composition, PDF/DOCX export, submission guidance, delivery, case identifiers, tracking, follow-up and outcome recording.

### Government information

Offices, departments, officers, representatives, schemes, benefits, services, laws, rules, bills, notifications, policies, projects, budgets and expenditure.

### Accountability

Citizen feedback, service experience, office performance signals, public representative information, government performance intelligence and public dashboards with appropriate safeguards.

### Knowledge contribution

Citizen corrections, evidence-backed contributions, expert review, volunteer review, institutional review and provenance/history.

### Participation ecosystem

Experts, volunteers, NGOs, civil-society organisations and institutions with role/permission controls.

### Emergency and resilience

SOS, trusted contacts, emergency delivery, resilient transport, mesh/gateway and satellite-capable pathways where technically and legally feasible.

### Decentralized/Web3

DApp access, decentralized identity/credentials, verifiable records, evidence provenance, citizen-controlled assets/records and alternative infrastructure where justified.

## 6. EXISTING FOUNDATION

The repository already contains substantial foundations including conversation/workflow/engine/domain/services/document/storage layers, Telegram integration, complaint/document/PDF capabilities, ratings/feedback services, legislative/constitutional/land routes, privacy/security components, and V2/V3/decentralized research implementations.

Each capability must be verified from current code and tests before being labelled production-ready.

## 7. STATUS MODEL

```text
VISION
 ↓
DESIGNED
 ↓
IMPLEMENTED
 ↓
FUNCTIONAL
 ↓
TESTED
 ↓
SECURITY-VERIFIED
 ↓
PRIVACY-VERIFIED
 ↓
PRODUCTION-READY
```

Legacy or experimental code does not automatically count as implemented capability.

## 8. DYNAMIC WEB

The Web is a first-class product surface. It will progressively expose shared Janavani capabilities rather than reproduce Telegram-specific logic.

The target Web is dynamic and ecosystem-capable: citizen workflows, information, documents, evidence, tracking, feedback, governance intelligence, multilingual/accessibility and public-facing views where appropriate.

## 9. MOBILE

Android and iOS are independent product surfaces consuming shared platform APIs/capabilities. They may support secure local state, notifications, evidence capture, location, low-bandwidth/offline workflows and SOS where appropriate.

## 10. MESSAGING

Telegram Bot, Telegram Mini App, WhatsApp and Messenger are independent access surfaces. The Telegram bot is an existing working foundation; the Mini App and other integrations should consume shared capabilities.

## 11. AI

AI is not a general chatbot product. It is controlled infrastructure for issue understanding, classification, language, retrieval, drafting, legal-information assistance and other bounded functions.

AI must be replaceable and must not become the sole source of truth.

## 12. GOVERNANCE INTELLIGENCE

The product can progressively connect:

```text
Public Source
   ↓
Government Commitment / Rule / Data
   ↓
Budget / Implementation / Service
   ↓
Citizen Experience
   ↓
Outcome
   ↓
Accountability / Learning
```

Provenance and verification are mandatory for public-facing claims.

## 13. PRODUCT PRINCIPLES

- Ecosystem-first
- Capability-first
- Interface-independent
- Privacy-first
- Evidence-aware
- Provenance-aware
- AI-optional and replaceable
- Decentralization where justified
- Open integration
- Citizen control
- Continuous verification

## 14. FINAL PRODUCT DEFINITION

Janavani is one citizen-governance ecosystem, not a sequence of unrelated MVPs. Individual interfaces and milestones are construction units inside that ecosystem.
