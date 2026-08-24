# 🇮🇳 JANAVANI — CITIZEN-GOVERNANCE ECOSYSTEM

**Status:** ACTIVE — ECOSYSTEM BUILD  
**Version:** 2.1  
**Date:** 24 August 2026  
**Repository:** `netzen-abm/janavani`

## What is Janavani?

Janavani is a **full citizen-governance ecosystem**: a privacy-first, safety-first, capability-oriented platform through which citizens can understand public problems, access verified government information, prepare lawful civic action, communicate with public institutions, track outcomes, contribute evidence and knowledge, and participate in public accountability.

Janavani is **not an MVP project**, not a Telegram-only project, not a website-only project, and not an AI chatbot. The target is the complete ecosystem.

The Dynamic Web is the **first active product-building surface**, but it is not the architectural center of gravity and must never become a dependency for other surfaces.

## Constitutional and civic foundation

Janavani operates within the constitutional and legal environment of India. The Preamble's **"We, the People of India"** framing is central to the citizen-centered purpose of the ecosystem.

Relevant constitutional principles include the **Articles 14, 19 and 21** framework (commonly described as the constitutional "golden triangle") where applicable to equality, freedoms, life, personal liberty and privacy-sensitive design. **Article 51A** contains the Fundamental Duties of citizens and may inform civic-education and participation context; it is not a standalone authorization for Janavani to exercise public authority. The **Bharatiya Sakshya Adhiniyam (BSA)** is statutory evidence law and must be treated as such, not as part of the Constitution.

Janavani is not a court, government authority, election authority, law-enforcement body, or substitute for qualified legal representation. Constitutional/statutory text, judicial decisions, authoritative government information, system-derived information, citizen information, expert review and AI assistance must remain distinguishable.

See `docs/JANAVANI_CONSTITUTIONAL_GOVERNANCE.md` for the canonical governance principles.

## Ecosystem surfaces

Janavani is designed to provide independent access through:

- Dynamic interactive Web application / WebApp
- Android application
- iOS application
- Telegram Bot / app
- Telegram Mini App
- WhatsApp integration
- Messenger integration
- Public/partner APIs
- DApp / Web3 capabilities where justified
- Offline/local capabilities where technically appropriate
- Decentralized, mesh, resilient and satellite-capable transports where technically and legally supported

All interfaces consume shared Janavani platform contracts. **No interface owns core business logic and no interface should depend on another interface for normal operation.** Users choose which surfaces and optional capabilities they want to use, subject to explicit safety, legal, destination, device and technical constraints.

## Capability-first model

The ecosystem is built around independently addressable capabilities rather than one monolithic application:

```text
Citizen / External Actor
          ↓
Independent Interface / Integration
          ↓
Shared Janavani Contracts
          ↓
Domain + Workflow + Capability Services
          ↓
Data + Trust + Provenance
          ↓
External Government / Civic Systems
```

A capability may use zero, one, or multiple implementations. An optional feature must not silently become a mandatory dependency for unrelated functionality.

## AI and intelligence capability families

AI is **optional, purpose-bound, replaceable infrastructure**. The ecosystem distinguishes user-facing capabilities from model/runtime families, including:

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
- Agentic AI / controlled tool-using agents
- Translation, speech and other multimodal capabilities as added

No single AI model/provider is the source of truth or a single point of failure. Critical workflows require appropriate deterministic or degraded paths.

## Privacy and safety

**Privacy by Design, Privacy by Default, Safety by Design and Safety by Default** are ecosystem invariants.

Janavani applies minimum necessary collection, purpose limitation, explicit consent where required, identity minimisation, user review/approval for consequential actions, evidence protection, provenance, access control, retention discipline, auditability and abuse prevention.

The system must be truthful about capability and delivery state: an attempted transmission is not a confirmed delivery, and an AI suggestion is not an official government determination.

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

## Failure-isolation principle

If one surface, capability, model, provider, transport or storage system fails, unrelated capabilities should continue whenever technically possible.

Examples:

- Web unavailable → Telegram/mobile/API can continue.
- Telegram unavailable → Web/mobile/API can continue.
- LLM unavailable → SLM/deterministic path can continue where appropriate.
- RAG unavailable → source-unavailable/degraded response, never invented facts.
- OCR/CV/VLM/SAM unavailable → manual/non-vision evidence path remains available where practical.
- Agent runtime unavailable → guided deterministic workflow remains available.
- Blockchain unavailable → ordinary civic workflows continue.
- Mesh/satellite unavailable → other configured paths or truthful queued state remain available.

## Documentation authority

Start with:

1. `docs/JANAVANI_NORTH_STAR.md` — strategic destination and civic purpose
2. `docs/JANAVANI_ECOSYSTEM_CHARTER.md` — current identity and ecosystem scope
3. `docs/JANAVANI_CONSTITUTIONAL_GOVERNANCE.md` — constitutional/legal framing, user choice and governance invariants
4. `docs/SOURCE_OF_TRUTH.md` — canonical architectural rules
5. `docs/JANAVANI_MASTER_ARCHITECTURE.md` — system architecture
6. `docs/JANAVANI_PRODUCT_LANDSCAPE.md` — capability and product landscape
7. `ROADMAP.md` — ecosystem construction sequence
8. `docs/MASTER_TASK_CHECKLIST.md` — master tasks and subtasks
9. `docs/CAPABILITY_REGISTRY.md` — capability status and ownership
10. `planning/` — active engineering contracts and detailed specifications
11. `docs/` — audits, architecture decisions, deployment and engineering records

Historical or superseded material belongs under `archive/` and must not be treated as current direction.

## Development rule

```text
North Star
      ↓
Ecosystem Charter
      ↓
Constitutional Governance
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

The present phase is **ecosystem foundation convergence + Dynamic Web active build**: establish capability/data/permission/transport/security contracts, verify runtime boundaries, build the Dynamic Web as the first active product surface, and progressively implement independent capabilities and interfaces without reducing the full ecosystem scope.

## Repository principle

GitHub is the primary engineering workspace and source for current implementation state. Local editors may be used operationally, but architectural decisions, documentation, code changes, tests, and evidence must be reconciled against GitHub.

## License

See `LICENSE`.
