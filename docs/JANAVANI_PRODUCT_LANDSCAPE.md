# JANAVANI — PRODUCT LANDSCAPE

**Status:** LOCKED — CURRENT PRODUCT LANDSCAPE  
**Version:** 2.1  
**Date:** 24 August 2026

## 1. PURPOSE

This document describes Janavani as a full product ecosystem: what capabilities exist, what is being built, and the intended system of interfaces and governance services.

It is not an MVP roadmap.

## 2. JANAVANI IN ONE SENTENCE

**Janavani is a privacy-first, safety-first citizen-governance ecosystem that helps citizens move from lived public problems to informed action, institutional response, follow-up, accountability and public learning through one shared capability platform exposed across independent interfaces.**

## 3. PRODUCT SURFACES

First-class surfaces include:

- Dynamic interactive Web / WebApp
- Android
- iOS
- Telegram Bot / app
- Telegram Mini App
- WhatsApp
- Messenger
- API
- DApp / Web3
- Decentralized/resilient transport interfaces where justified
- Offline/local capabilities where supported

Users choose which available surface and optional capability they want to use. No optional surface becomes a mandatory dependency for unrelated functionality.

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

Conversation, guided workflows, forms, session/state, language, accessibility and user-controlled capability selection.

### Intelligence

Issue understanding, classification, department/authority identification, office intelligence, location intelligence, legal-information assistance, retrieval and grounded AI.

### Civic action

Complaint, grievance, RTI, representation, petition, objection, appeal, follow-up, escalation and other lawful civic workflows.

### Evidence

Photo, video, document, voice where appropriate, OCR, Computer Vision, VLM/SAM-assisted analysis, metadata, provenance, verification and review.

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

## 6. AI / MODEL LANDSCAPE

AI is optional, purpose-bound and replaceable. Distinguish product capabilities from implementation/model families:

- OCR
- Computer Vision (CV)
- SAM / segmentation
- VLM / vision-language models
- SLM / small language models
- LLM / large language models
- MLM / masked-language-model family where useful
- MoE / mixture-of-experts architectures
- LAM / language-action models
- RAG / retrieval-augmented generation
- Agentic AI / controlled tool-using workflows
- Translation, speech and other multimodal services

A capability may use zero, one, or multiple model families. Model/provider failure must not disable unrelated capabilities.

## 7. CONSTITUTIONAL / CIVIC ORIENTATION

Janavani operates within India's constitutional and legal environment. The Preamble's **"We, the People of India"** framing is central to its citizen-centered purpose. Articles 14, 19 and 21 provide a relevant constitutional framework for equality, freedoms, life, personal liberty and privacy-sensitive design where applicable. Article 51A contains citizens' Fundamental Duties and may inform civic education/participation; it is not a standalone authorization for Janavani to exercise public authority. The Bharatiya Sakshya Adhiniyam (BSA) is statutory evidence law.

Janavani is not a court, government authority, election authority, law-enforcement body, or substitute for qualified legal representation. Source classes must remain distinguishable: constitutional/statutory text, judicial decisions, authoritative government information, citizen information, expert review, system-derived information and AI assistance.

## 8. EXISTING FOUNDATION

The repository contains foundations including conversation/workflow/engine/domain/services/document/storage layers, Telegram integration, complaint/document/PDF capabilities, ratings/feedback services, legislative/constitutional/land routes, privacy/security components, and V2/V3/decentralized research implementations.

Each capability must be verified from current code and tests before being labelled production-ready.

## 9. STATUS MODEL

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

## 10. DYNAMIC WEB

The Web is the first active product-building surface and a first-class product surface. It will progressively expose shared Janavani capabilities rather than reproduce Telegram-specific logic.

The target Web is dynamic and ecosystem-capable: citizen workflows, information, documents, evidence, tracking, feedback, governance intelligence, multilingual/accessibility and public-facing views where appropriate.

## 11. MOBILE

Android and iOS are independent product surfaces consuming shared platform APIs/capabilities. They may support secure local state, notifications, evidence capture, location, low-bandwidth/offline workflows and SOS where appropriate.

## 12. MESSAGING

Telegram Bot, Telegram Mini App, WhatsApp and Messenger are independent access surfaces. The Telegram bot is an existing working foundation; the Mini App and other integrations should consume shared capabilities.

## 13. AI

AI is not a general chatbot product. It is controlled infrastructure for issue understanding, classification, language, retrieval, drafting, legal-information assistance, document understanding, evidence analysis and other bounded functions.

AI must be replaceable and must not become the sole source of truth. Critical workflows need appropriate deterministic/degraded paths.

## 14. GOVERNANCE INTELLIGENCE

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

## 15. PRODUCT PRINCIPLES

- Ecosystem-first
- Capability-first
- User-choice-first
- Interface-independent
- Privacy by Design
- Privacy by Default
- Safety by Design
- Safety by Default
- Evidence-aware
- Provenance-aware
- AI-optional and replaceable
- Failure-isolated
- Decentralization where justified
- Open integration
- Citizen control
- Continuous verification

## 16. FINAL PRODUCT DEFINITION

Janavani is one citizen-governance ecosystem, not a sequence of unrelated MVPs. Individual interfaces, capabilities, AI/model families, transports and milestones are replaceable construction units inside that ecosystem.
