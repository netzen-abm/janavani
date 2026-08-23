# 🇮🇳 JANAVANI — MASTER ARCHITECTURE

**Status:** ARCHITECTURE LOCK — DRAFT FOR IMPLEMENTATION
**Version:** 1.0
**Date:** 23 August 2026
**Authority:** Master architecture specification for the full Janavani ecosystem

---

## 1. Purpose

Janavani is a citizen-governance ecosystem, not an AI chatbot and not a single-interface application.

The architecture must support a fully functioning ecosystem in which citizens choose how they access Janavani and which capabilities they use.

The ecosystem includes, subject to implementation and regulatory verification:

- Dynamic Web application
- Android application
- iOS application
- Telegram Bot
- Telegram Mini App
- WhatsApp integration
- Messenger integration
- Web3 DApp
- Freenet/decentralized capability
- Offline/local operation
- Mesh communication
- Satellite communication where supported and legally authorised

No interface, AI provider, transport, storage system, blockchain, Freenet node, or external service may become a mandatory single point of failure for unrelated Janavani capabilities.

---

## 2. Core Architectural Principle

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
     Messenger / DApp          Freenet / Web3
```

Interfaces consume capabilities. Capabilities do not depend on interfaces.

A Telegram failure must not break Web.
A Web failure must not break Telegram.
An AI provider failure must not break non-AI capabilities.
A blockchain failure must not break SOS.
A Freenet failure must not break standard operation.

---

## 3. Capability-First Architecture

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

A capability descriptor must declare identity requirements, consent requirements, AI requirements, network requirements, offline support, supported channels, evidence requirements, and failure behavior.

---

## 4. Intelligence Architecture

AI is an optional controlled intelligence layer.

```text
OCR / Vision / ASR
        |
        v
Local / SLM / RAG
        |
        v
Optional LLM
        |
        v
Purpose-bound Agentic AI
```

AI must not become an unrestricted general chat feature inside Janavani.

AI is used for designated purposes such as:

- issue structuring;
- document drafting;
- document review;
- legal-information retrieval;
- Constitution-based analysis;
- bill/act/ordinance analysis;
- OCR and document understanding;
- multilingual assistance;
- evidence classification;
- government-information discovery.

Every AI capability requires deterministic/non-AI fallback where practical.

---

## 5. Constitutional and Civic Knowledge Foundation

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

AI outputs must identify sources and must not present generated analysis as a court ruling or legal advice.

---

## 6. Document Platform

Janavani must support purpose-bound generation of:

- complaints;
- grievances;
- RTI applications;
- representations;
- petitions;
- objections;
- appeals;
- follow-up letters;
- escalation letters;
- whistleblower submissions;
- emergency reports;
- other approved civic documents.

Generated documents must support:

- To address — full postal address;
- To email address;
- CC addresses — full postal address and email where available;
- From address area left blank unless the user chooses otherwise;
- subject;
- references;
- facts;
- legal/policy basis;
- requests;
- enclosures;
- signature area;
- submission guidance.

Default export formats are PDF and DOCX.

The user must be able to correct an address and submit a correction to Janavani's data-quality system.

---

## 7. User-Contributed Corrections

Citizen corrections are treated as candidate data improvements, not automatically authoritative facts.

```text
User correction
      |
      v
Candidate change
      |
      v
Validation / source comparison
      |
      +--> Accepted
      +--> Rejected
      +--> Needs expert review
```

Corrections may be reviewed by authorised subject experts, volunteers, institutions, government sources, or other trusted evidence sources.

Gamification may reward verified contributions, but must never reward volume over accuracy.

---

## 8. Expert and Volunteer Network

Participation may be available to:

- individuals;
- subject experts;
- societies;
- communities;
- NGOs;
- institutions;
- professional organisations;
- academic/research bodies;
- verified volunteers.

Access is user-controlled and permission-based.

Expert status must not automatically confer authority to make final legal or governmental determinations.

---

## 9. Accountability and Government Intelligence

The ecosystem may support structured evaluation of:

- government offices;
- officers and public servants;
- departments;
- MPs;
- MLAs;
- government service performance;
- complaint responsiveness;
- resolution patterns;
- public schemes and benefits;
- central and state government performance.

Public ratings must include safeguards against defamation, brigading, manipulation, retaliation, false claims, and publication of unnecessary personal information.

Allegations must remain distinguishable from verified findings.

---

## 10. Emergency & Public Safety

`JNV-CAP-SOS` is a core production capability.

It contains two independent systems:

1. Personal SOS — citizen-triggered.
2. Government emergency alerts — user-controlled opt-in/opt-out.

Personal SOS may notify selected:

- friends;
- relatives;
- trusted contacts;
- emergency authorities where supported and authorised.

Government alerts must preserve official provenance and must never be represented as AI-generated authority.

---

## 11. SOS Transport Architecture

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
                   / Meshtastic          transport
      |                   |                    |
      +-------------------+--------------------+
                          |
                   STORE & FORWARD
                          |
                   Gateway / Relay
                          |
                   Destination
```

Mesh and satellite are current architecture requirements, not deferred concepts.

A transport abstraction must allow multiple providers and protocols without changing the SOS capability.

No SOS delivery may be reported as successful merely because transmission was attempted.

Required delivery states include:

`CREATED -> QUEUED -> TRANSMITTING -> SENT -> RECEIVED -> ACKNOWLEDGED`

---

## 12. Offline and Local Operation

Capabilities should declare whether they support:

- offline operation;
- local AI;
- local storage;
- delayed synchronization;
- mesh transport;
- decentralized transport.

The system must be honest about physical communication limits. If no communication path exists, Janavani can securely store and retry; it cannot falsely claim remote delivery.

---

## 13. Evidence and Provenance

Evidence may include:

- documents;
- photographs;
- video;
- audio;
- OCR output;
- timestamps;
- optional location;
- source references;
- cryptographic hashes.

Evidence anchoring to blockchain or decentralized infrastructure is optional and must never be a critical dependency for civic or SOS workflows.

Archive is preferred over deletion when retention is appropriate. Deletion requires an explicit retention/privacy basis.

---

## 14. Financial Transparency

The ecosystem may publish live operating expenditure information by category and provide a contribution mechanism.

Financial principles:

- full disclosure on demand;
- auditable records;
- clear operating reserve policy;
- separation of restricted and unrestricted funds;
- public contributor display controlled by the contributor;
- anonymous display options;
- public financial reporting without exposing unnecessary personal information.

The operating reserve policy should be based on demonstrated operating risk and governance requirements rather than an arbitrary fixed amount.

---

## 15. Identity and Privacy

Identity linking across interfaces is:

- optional;
- explicit;
- user-controlled;
- revocable;
- auditable.

Government alert opt-in does not imply location tracking.

SOS location sharing is purpose-bound and user-controlled.

Citizen data should be minimised and protected according to purpose.

---

## 16. Infrastructure Independence

The architecture must avoid mandatory dependence on any one:

- AI vendor;
- cloud provider;
- database;
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

## 17. Production Rule

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

## 18. Current Architecture Decision

The immediate engineering objective is not to add arbitrary features to the existing prototype.

The objective is to reconcile the existing repository with this architecture through controlled, auditable changes.

No destructive deletion is permitted merely because code is old. Deprecated material is archived after replacement, imports are removed, tests pass, and runtime behavior is verified.

---

**END — JANAVANI MASTER ARCHITECTURE**
