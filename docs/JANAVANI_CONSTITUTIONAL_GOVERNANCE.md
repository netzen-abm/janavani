# 🇮🇳 JANAVANI — CONSTITUTIONAL GOVERNANCE & USER CHOICE

**Status:** CANONICAL — GOVERNANCE PRINCIPLES
**Version:** 1.0
**Date:** 24 August 2026

## 1. Purpose

Janavani is a citizen-governance technology ecosystem intended to help people understand public problems, access authoritative information, prepare lawful civic action, preserve evidence and provenance, communicate with public institutions, track outcomes, and participate in accountable public life.

Janavani operates within the constitutional and legal environment of India. It is a technology platform, not a constitutional office, court, government authority, election authority, law-enforcement body, or substitute for qualified legal representation.

## 2. Constitutional framing

The Preamble's opening — **"We, the People of India"** — is a foundational civic framing principle for Janavani's citizen-centered design.

The constitutional **Articles 14, 19 and 21** framework, commonly described as the Constitution's "golden triangle", is relevant to equality, freedoms and life/personal-liberty-sensitive design questions where applicable. Janavani must rely on the Constitution, legislation, authoritative government sources and applicable judicial interpretation rather than treating a slogan or simplified summary as a legal determination.

**Article 51A** contains the Fundamental Duties of citizens. Janavani may use relevant Fundamental Duties as civic-education and participation context, but Article 51A must not be represented as a standalone statutory authorization for Janavani to exercise public authority.

The **Bharatiya Sakshya Adhiniyam (BSA)** is statutory evidence law. It may be relevant to evidence-oriented workflows, but it is not part of the Constitution and must not be described as such.

Janavani should distinguish:

1. constitutional text;
2. legislation/statutory law;
3. rules, regulations and notifications;
4. judicial decisions and legal interpretation;
5. authoritative government information;
6. Janavani system-derived information;
7. citizen-provided information;
8. expert-reviewed material; and
9. AI-assisted explanation or suggestion.

## 3. Citizen choice

Janavani is capability-first and user-controlled.

A citizen may choose:

- Web / WebApp;
- Android;
- iOS;
- Telegram Bot;
- Telegram Mini App;
- WhatsApp;
- Messenger;
- API/integration access;
- DApp/Web3 features;
- local/offline functionality;
- optional AI assistance;
- optional agentic workflows;
- optional decentralized/resilient transports where supported.

Optional capabilities must not be silently forced on the user. The system should explain material consequences, permissions, data use, and limitations before consequential activation.

Safety, legal, destination, device, network, emergency, and technical constraints may limit available choices. Such constraints must be explicit rather than hidden.

## 4. Privacy and safety by design/default

Privacy and safety are architecture invariants, not optional add-ons.

- Privacy by Design.
- Privacy by Default.
- Safety by Design.
- Safety by Default.
- Minimum necessary collection.
- Purpose limitation.
- Explicit consent where required.
- User review and approval for consequential actions.
- Identity minimisation and optional cross-channel linking.
- Evidence protection and provenance.
- Retention and deletion discipline.
- Auditability without unnecessary exposure.
- Honest delivery and system-status reporting.

The safest default should not silently remove legitimate user choice. Defaults should minimise unnecessary exposure while preserving an understandable path to capabilities the user deliberately enables.

## 5. Independent access surfaces

Every access surface is an independent consumer of shared Janavani contracts.

```text
Web / WebApp ───────┐
Android ────────────┤
iOS ────────────────┤
Telegram Bot ───────┤
Telegram Mini App ──┤
WhatsApp ───────────┤
Messenger ──────────┤→ Shared Janavani capability contracts
DApp / Web3 ────────┤
API / integrations ─┘
```

No surface may depend on another surface for normal operation. A failure of Web must not disable Telegram, and a Telegram outage must not disable Web, mobile, API or DApp capabilities.

## 6. Capability independence

Capabilities are independently deployable or replaceable where practical and have explicit contracts for:

- identity;
- permissions/consent;
- inputs/outputs;
- data/provenance;
- AI dependence;
- network/transport requirements;
- offline/local support;
- failure behavior;
- security/privacy requirements;
- completion tests.

A capability may depend on shared contracts and foundational infrastructure, but it must not create an unnecessary hard dependency on an unrelated feature or channel.

## 7. AI and model taxonomy

AI is optional, purpose-bound and replaceable. The architecture distinguishes **user-facing capabilities** from **model/runtime families**.

### AI/model families and technologies

- **OCR** — optical character recognition/document text extraction.
- **Computer Vision (CV)** — visual detection, classification and analysis.
- **SAM / segmentation models** — segmentation and object-mask capabilities.
- **VLM** — vision-language model family for multimodal understanding.
- **SLM** — small/local language-model family for privacy, offline and resource-constrained operation.
- **LLM** — large language-model family for approved higher-capability language tasks.
- **MLM** — masked-language-model family where appropriate for language representation or specialised inference.
- **MoE** — mixture-of-experts model architecture for routing specialised model capacity.
- **LAM** — language-action model family for controlled action-oriented reasoning.
- **RAG** — retrieval-augmented generation architecture for grounded, source-linked information access.
- **Agentic AI** — controlled tool-using workflows that operate under explicit permissions, limits and human-approval gates.

These are not automatically separate products. They are implementation families that may support one or more Janavani capabilities.

A capability may use no AI, one model family, several model families, or a deterministic implementation. Model/provider failure must not take down unrelated civic workflows.

## 8. Failure isolation

Representative invariants:

- LLM unavailable → SLM/deterministic path where appropriate.
- RAG unavailable → source-unavailable/degraded response; never invented facts.
- OCR unavailable → manual evidence/document path remains available where practical.
- CV/VLM/SAM unavailable → non-vision evidence path remains available.
- Agent runtime unavailable → guided deterministic workflow remains available.
- Telegram unavailable → Web/mobile/API/other channels continue.
- Web unavailable → Telegram/mobile/API/other channels continue.
- Blockchain unavailable → ordinary civic workflows continue.
- Mesh unavailable → ordinary Internet/local paths continue.
- Satellite unavailable → another configured path or truthful queued state; never false delivery.
- One storage/provider dependency unavailable → approved alternate/recovery path where supported.

## 9. Human authority and AI limits

AI may assist with understanding, classification, retrieval, drafting, translation, document understanding, evidence classification and other approved tasks.

AI must not fabricate:

- legal provisions;
- government authorities;
- evidence;
- official actions;
- delivery acknowledgements;
- emergency alerts;
- verification states.

Consequential external actions require appropriate human confirmation and permission controls.

## 10. Constitutional/legal source discipline

Where Janavani provides civic or legal-information assistance, it should prefer authoritative sources and preserve source identity, date/version and verification state.

The system must clearly label when content is:

- direct authoritative text;
- source-backed summary;
- Janavani-derived analysis;
- expert review;
- AI-assisted suggestion; or
- unverified citizen information.

Janavani should never present an AI-generated answer as a court ruling, official government determination or guaranteed legal outcome.

## 11. Final principle

> **We, the People of India** is the civic framing; the Constitution and applicable law define the legal environment; Janavani provides technology that helps citizens exercise lawful civic agency with privacy, safety, provenance, user choice and resilience.

The ecosystem remains the destination. Individual applications, channels, AI models and transports are replaceable access and implementation mechanisms inside that ecosystem.
