# 🇮🇳 JANAVANI — MASTER ARCHITECTURE

**Status:** ARCHITECTURE LOCK — IMPLEMENTATION BASELINE  
**Version:** 1.1  
**Date:** 24 August 2026  
**Authority:** Master architecture specification for the full Janavani ecosystem

---

## 1. Purpose

Janavani is a citizen-governance ecosystem, not an AI chatbot and not a single-interface application.

The architecture supports a fully functioning ecosystem in which citizens choose how they access Janavani and which capabilities they use.

The ecosystem includes, subject to implementation and regulatory verification:

- Dynamic interactive Web application / WebApp
- Android application
- iOS application
- Telegram Bot / app
- Telegram Mini App
- WhatsApp integration
- Messenger integration
- Public/partner APIs
- Web3 DApp
- Decentralized capabilities
- Offline/local operation
- Mesh communication
- Satellite communication where supported and legally authorised

No interface, AI provider/model, transport, storage system, blockchain, decentralized node, or external service may become a mandatory single point of failure for unrelated Janavani capabilities.

---

## 2. Constitutional and civic foundation

Janavani operates within India's constitutional and legal environment.

- The Preamble's **"We, the People of India"** framing is a foundational civic principle.
- Articles **14, 19 and 21** form a relevant constitutional framework for equality, freedoms, life, personal liberty and privacy-sensitive design where applicable.
- **Article 51A** contains the Fundamental Duties of citizens. It may inform civic education and participation, but it is not a standalone authorization for Janavani to exercise public authority.
- The **Bharatiya Sakshya Adhiniyam (BSA)** is statutory evidence law and must not be described as constitutional text.

Janavani is not a court, government authority, election authority, law-enforcement body, or substitute for qualified legal representation.

Constitutional text, legislation, judicial decisions, authoritative government information, citizen reports, expert review, system-derived information and AI assistance must remain distinguishable.

---

## 3. Core architectural principle

```text
                    JANAVANI CORE
                         |
                  CAPABILITY LAYER
                         |
             +-----------+-----------+
             |                       |
        CHANNEL ADAPTERS       INFRASTRUCTURE
             |                       |
     Web / Android / iOS       Internet / Mesh
     Telegram / WhatsApp       Satellite / Local
     Messenger / DApp          Decentralized / Web3
```

Interfaces consume capabilities. Capabilities do not depend on interfaces.

A Telegram failure must not break Web.  
A Web failure must not break Telegram.  
An AI provider/model failure must not break non-AI capabilities.  
A blockchain/decentralized-network failure must not break SOS or ordinary civic operation.  
A transport failure must never be represented as successful delivery.

---

## 4. User-choice architecture

Janavani is **capability-first and user-controlled**.

Users may choose available surfaces and optional capabilities. The system must not silently force Web3, AI, agentic automation, a particular messaging platform, a particular transport, or cross-channel identity linking when those features are optional.

Material safety, legal, destination, device, network and emergency constraints must be explicit.

A capability contract should declare:

- identity requirement;
- permission/consent requirement;
- data minimisation requirements;
- AI/model requirements;
- network/transport requirements;
- offline/local support;
- supported channels;
- supported transports;
- inputs/outputs;
- provenance/evidence requirements;
- failure/degraded behavior;
- security/privacy requirements;
- completion tests.

---

## 5. Capability-first architecture

Every major Janavani function is a capability with an explicit contract.

Examples:

- `CIVIC.COMPLAINT.DRAFT`
- `CIVIC.GRIEVANCE.DRAFT`
- `CIVIC.RTI.DRAFT`
- `CIVIC.PETITION.DRAFT`
- `CIVIC.OBJECTION.DRAFT`
- `GOVERNMENT.BILL.ANALYZE`
- `GOVERNMENT.SCHEME.SEARCH`
- `GOVERNMENT.OFFICE.SEARCH`
- `GOVERNMENT.OFFICER.REVIEW`
- `GOVERNMENT.PERFORMANCE.EVALUATE`
- `EVIDENCE.CAPTURE`
- `EVIDENCE.PROVENANCE`
- `DOCUMENT.GENERATE`
- `DOCUMENT.EXPORT`
- `SOS.PERSONAL`
- `SOS.GOVERNMENT_ALERT`
- `WHISTLEBLOWER.SUBMIT`
- `EXPERT.REVIEW`

A capability may have multiple implementations. The capability contract is stable while model, provider, transport, storage and presentation implementations remain replaceable.

---

## 6. Intelligence and AI/model architecture

AI is an optional controlled intelligence layer.

```text
OCR / CV / SAM / ASR
        |
        v
VLM / SLM / MLM
        |
        v
RAG / LLM / MoE
        |
        v
LAM / Purpose-bound Agentic AI
```

The list represents model/architecture families and intelligence mechanisms, not a mandatory processing chain. A capability may use one, several, or none of them.

### Model/runtime families

- **OCR** — optical character recognition.
- **Computer Vision (CV)** — visual detection/classification/analysis.
- **SAM** — segmentation/object-mask models.
- **VLM** — vision-language models.
- **SLM** — small/local language models.
- **LLM** — large language models.
- **MLM** — masked-language-model family where useful.
- **MoE** — mixture-of-experts architecture.
- **LAM** — language-action model family.
- **RAG** — retrieval-augmented generation with source grounding.
- **Agentic AI** — controlled tool-using workflows with explicit permissions and human approval.

AI may support issue structuring, document drafting/review, legal-information retrieval, constitutional/statutory source analysis, OCR/document understanding, multilingual assistance, evidence classification and government-information discovery.

AI must not fabricate authorities, legal provisions, evidence, official actions, emergency alerts, delivery acknowledgements or verification states.

Every critical AI-assisted workflow requires an appropriate deterministic or degraded path where practical.

---

## 7. Failure-isolation architecture

Representative failure domains:

```text
Channel failure       → other channels continue
Model failure         → alternate model/deterministic path
Provider failure      → adapter fallback/degraded state
RAG failure           → source-unavailable state
OCR/CV failure        → manual evidence path
Agent failure         → guided workflow
Transport failure     → alternate path / truthful queue
Blockchain failure    → normal non-Web3 operation
Storage failure       → recovery/degraded path
```

External providers require bounded timeouts, bounded retries, circuit breakers, health state, fallback routing and observability where appropriate.

Queues/brokers should isolate slow or unavailable capabilities from request-serving paths. Durable asynchronous work must have retry and dead-letter/recovery behavior.

---

## 8. Constitutional and Civic Knowledge Foundation

JanaVani's civic intelligence must be grounded in authoritative Indian constitutional and statutory sources.

The constitutional foundation includes particular emphasis on:

- Preamble;
- Constitution of India;
- Fundamental Rights and relevant constitutional provisions;
- constitutional structure and separation of powers;
- applicable statutory law;
- Right to Information framework;
- Bharatiya Sakshya Adhiniyam (BSA), where relevant to evidence-related workflows;
- applicable rules, regulations, notifications and authoritative government sources.

The Preamble's "We, the People of India" principle is a central civic framing principle, but Janavani must distinguish constitutional philosophy from the precise legal authority of any particular provision.

Article 51A should be represented as Fundamental Duties of citizens, not as a grant of public authority to Janavani.

AI outputs must identify sources and must not present generated analysis as a court ruling or legal advice.

---

## 9. Document platform

Janavani must support purpose-bound generation of complaints, grievances, RTI applications, representations, petitions, objections, appeals, follow-up letters, escalation letters, whistleblower submissions, emergency reports and other approved civic documents.

Generated documents support address, subject, references, facts, legal/policy basis, requests, enclosures, signature area and submission guidance. Default export formats are PDF and DOCX.

The user must be able to correct an address and submit a correction to Janavani's data-quality system.

---

## 10. Evidence and provenance

Evidence may include documents, photographs, video, audio, OCR output, timestamps, optional location, source references and cryptographic hashes.

Evidence anchoring to blockchain or decentralized infrastructure is optional and must never be a critical dependency for civic or SOS workflows.

Citizen reports remain distinguishable from verified findings.

---

## 11. Emergency and public safety

`JNV-CAP-SOS` is a core production capability.

It contains two independent systems:

1. Personal SOS — citizen-triggered.
2. Government emergency alerts — user-controlled opt-in/opt-out.

Government alerts must preserve official provenance and must never be represented as AI-generated authority.

---

## 12. SOS transport architecture

```text
                         SOS
                          |
                  SOS ROUTING ENGINE
                          |
      +-------------------+--------------------+
      |                   |                    |
   Internet              Mesh              Satellite
      |                   |                    |
 Cellular/WiFi     Reticulum / LoRa     Supported satellite
      |            / Meshtastic          transport
      +-------------------+--------------------+
                          |
                   STORE & FORWARD
                          |
                   Gateway / Relay
                          |
                   Destination
```

Mesh and satellite are architecture requirements for appropriate resilience use cases, not mandatory dependencies for ordinary operation.

No SOS delivery may be reported as successful merely because transmission was attempted.

Required delivery states include:

`CREATED -> QUEUED -> TRANSMITTING -> SENT -> RECEIVED -> ACKNOWLEDGED`

---

## 13. Offline and local operation

Capabilities should declare whether they support offline operation, local AI, local storage, delayed synchronization, mesh transport or decentralized transport.

If no communication path exists, Janavani can securely store and retry; it cannot falsely claim remote delivery.

---

## 14. Identity, privacy and safety

Identity linking across interfaces is optional, explicit, user-controlled, revocable and auditable.

Privacy and safety are architecture invariants:

- Privacy by Design;
- Privacy by Default;
- Safety by Design;
- Safety by Default;
- minimum necessary collection;
- purpose limitation;
- consent;
- identity minimisation;
- secure evidence handling;
- retention controls;
- access auditability;
- threat modelling;
- abuse prevention;
- secure recovery.

---

## 15. Infrastructure independence

The architecture must avoid mandatory dependence on any one:

- AI vendor/model family;
- cloud provider;
- database/storage backend;
- messaging platform;
- decentralized network;
- blockchain;
- satellite provider;
- government integration;
- identity provider.

Adapters must expose explicit health states such as:

`AVAILABLE`, `DEGRADED`, `UNAVAILABLE`, `NOT_CONFIGURED`.

Mock implementations must never report themselves as production success.

---

## 16. Dynamic Web construction priority

The Dynamic Web is the first active product-building surface and must be implemented as a complete, interactive, testable product surface against shared contracts.

The Web must not become a dependency for Android, iOS, Telegram, WhatsApp, Messenger, DApp or API consumers.

The first complete Web vertical slice should cover issue understanding → authority → action/draft → evidence → citizen review → submission/tracking, while remaining extensible to the broader ecosystem lifecycle.

---

## 17. Production rule

Before replacing existing implementations, define and review:

1. capability contract;
2. data contract;
3. permission/consent contract;
4. transport contract;
5. failure policy;
6. test requirements;
7. security/privacy requirements.

Only then implement or replace code.

---

## 18. Current architecture decision

The immediate engineering objective is to reconcile the existing repository with this architecture through controlled, auditable changes while actively building the Dynamic Web.

No destructive deletion is permitted merely because code is old. Deprecated material is archived after replacement, imports are removed, tests pass, runtime behavior is verified, and documentation is reconciled.

---

**END — JANAVANI MASTER ARCHITECTURE**
