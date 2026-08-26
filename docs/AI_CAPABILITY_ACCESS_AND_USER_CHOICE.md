# Janavani AI Capability Access & User Choice Contract

**Status:** CANONICAL ARCHITECTURE POLICY
**Date:** 26 August 2026

## 1. Core rule

Janavani's ecosystem is intended to contain the complete set of approved capabilities and access surfaces. **Optional means optional for the user, not optional for the ecosystem.**

A capability may be disabled, declined, unavailable, unsuitable for a particular circumstance, or not selected by a user. That does not mean the capability should be omitted from the Janavani ecosystem architecture when it is part of the approved product scope.

The ecosystem should therefore provide the capability through a governed contract, while each user decides whether, when and how to use it, subject to safety, legal, privacy, device, network and emergency constraints.

## 2. Applies to all access surfaces

The rule applies consistently to:

- Dynamic Web / WebApp
- Android
- iOS
- Telegram Bot
- Telegram Mini App
- WhatsApp
- Messenger
- DApp / Web3
- Public/API integrations
- Future approved channels

No access surface should silently remove an ecosystem capability merely because the capability is optional for an individual user.

## 3. AI and Agentic AI

AI is an ecosystem capability, not a mandatory dependency of every workflow and not a feature owned by any particular client.

The ecosystem should support governed AI capabilities including, where approved:

- OCR
- Computer Vision / document understanding
- VLM
- SLM / local AI
- LLM
- RAG
- translation and speech
- other approved multimodal intelligence
- controlled Agentic AI

The user may choose whether to invoke an AI capability. Capability routing may also determine that AI is unnecessary for a particular task and use a deterministic path instead.

## 4. Circumstance-based capability selection

A user-facing capability may use zero, one or multiple intelligence mechanisms according to:

- task requirements
- user choice and consent
- privacy mode
- local-device availability
- network availability
- capability health
- source/grounding requirements
- safety and legal constraints
- workflow permissions

The UI should expose useful actions such as "Improve draft", "Help me understand", "Find the appropriate authority", "Check this document", "Suggest recipients", "Translate" and "Review before submission" rather than requiring users to understand model terminology.

## 5. Document and letter drafting

Document generation must remain usable without AI where practical. AI may assist with:

- drafting
- rewriting
- grammar and clarity
- translation
- summarisation
- chronology extraction
- missing-information detection
- document review
- recipient suggestions

The deterministic document composition/export path remains available as a fallback.

## 6. To / CC intelligence

For civic documents, AI may help identify the likely purpose, jurisdiction and appropriate recipient categories. It must not invent official addresses or contact details.

Verified directory/source data must establish official To/CC addresses and contact information where available. The user must be able to inspect, edit and approve recipients before consequential use.

## 7. Agentic AI boundary

Agentic AI may execute approved multi-step tasks through explicit capability/tool contracts. It must use scoped permissions and truthful state reporting.

Consequential external actions such as submission, sending messages, signing transactions, disclosure of sensitive information or other irreversible actions require the appropriate human confirmation gate.

Agentic AI failure must not block an equivalent deterministic or guided workflow where practical.

## 8. Provider independence

AI providers and model families are replaceable implementations. No specific provider, model, cloud service or agent runtime may become the mandatory source of truth or a single point of failure for core civic workflows.

The architecture should support local-first, provider-independent and degraded/fallback operation where practical.

## 9. Privacy and consent

Choosing to use an AI capability is not blanket consent to unrelated data collection or disclosure. Data sent to an external AI service must be minimized to the purpose of the request and governed by the applicable privacy/consent contract.

Local AI should be preferred where appropriate for privacy-sensitive or offline tasks, without making local AI mandatory where the user chooses another approved route.

## 10. Ecosystem completeness vs user choice

This distinction is normative:

| Scope | Meaning |
|---|---|
| Ecosystem | Should contain the approved capability and its governed contract |
| Access surface | Should expose the capability when technically and legally supported |
| User | Decides whether to use/enable/invoke the optional capability |
| Workflow | May use AI, deterministic logic, or both depending on circumstance |
| Consequential action | Requires appropriate permission and human confirmation |

Therefore, documentation must not use "optional" to mean "out of scope", "not implemented in the ecosystem", or "not required to provide the capability" when the capability is part of the approved ecosystem scope.

## 11. Canonical wording

Use the following wording in future architecture/product documentation:

> **Optional is a user-choice property, not an ecosystem-coverage property. Janavani should provide the complete approved capability ecosystem; users decide which capabilities they use, enable or invoke, subject to applicable safety, legal, privacy, device, network and emergency constraints.**

## 12. Relationship to capability contracts

Each ecosystem capability should have an explicit contract defining purpose, actor, permission/consent, identity requirements, AI dependency, offline/local support, supported channels, transports, inputs, outputs, provenance, failure behavior, completion tests and status.

This contract is the basis for exposing the same capability consistently across channels while keeping channel implementations independent.
