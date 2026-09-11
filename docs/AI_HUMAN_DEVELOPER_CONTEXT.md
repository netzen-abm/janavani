# JANAVANI — AI / HUMAN / DEVELOPER CONTEXT

**Status:** CANONICAL ORIENTATION — NOT A SUBSTITUTE FOR SOURCE-OF-TRUTH DOCUMENTS
**Version:** 1.0
**Date:** 11 September 2026
**Purpose:** Give AI agents, human developers, reviewers and maintainers one concise, current understanding of the decisions reached during Janavani architecture and repository convergence work.

> This document records the current shared understanding. It does not override the authority hierarchy in `docs/DOCUMENTATION_INDEX.md`.

---

## 1. JANAVANI IDENTITY

Janavani is **The Infrastructure of Citizen Voice**: a complete citizen-governance ecosystem for meaningful citizen participation and civic action.

Janavani is not:

- a Telegram bot;
- a chatbot;
- a complaint-only application;
- an RTI-only tool;
- a document generator;
- a WebApp-only product;
- a blockchain project;
- an AI product;
- an MVP whose scope ends at one workflow.

Those are interfaces, capabilities, technologies or construction stages inside one ecosystem.

The constitutional civic framing includes the Preamble's **"We, the People of India"** principle. Janavani does not exercise public authority and is not a court, government authority, election authority, law-enforcement body or substitute for qualified legal representation.

---

## 2. ONE ECOSYSTEM — MANY INDEPENDENT SURFACES

The ecosystem provides shared capabilities. Access surfaces consume those capabilities.

```text
                     JANAVANI
                        |
               SHARED INFRASTRUCTURE
                        |
        +---------------+---------------+
        |               |               |
      CASE           EVIDENCE        AUTHORITY
        |               |               |
     DOCUMENT        CONSENT        JURISDICTION
        |               |               |
      SUBMIT          TRACK          OUTCOME
        |               |               |
        +---------------+---------------+
                        |
                 POLICY / TRUST
                        |
              PROVIDERS / ADAPTERS
                        |
        +---------------+---------------+
        |       |       |       |       |
       Web   Telegram  Mobile  DApp   Messaging
```

Current and future surfaces include Dynamic Web/WebApp, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, API, DApp/Web3 and resilient/local interfaces where justified.

No surface owns shared business logic. No surface normally depends on another surface for ordinary operation.

---

## 3. SHARED-INFRASTRUCTURE-FIRST RULE

Every new feature, function, skill, tool, service, AI function, agent function or technology integration must first be evaluated as reusable shared infrastructure.

The design question is:

> **Can another Janavani access surface consume this without rebuilding the capability?**

If not, redesign the boundary before adding interface-specific logic, unless an explicit ADR records a justified exception.

Reusable infrastructure includes, where applicable:

- domain objects and rules;
- workflows and workflow steps;
- application services;
- capability contracts;
- repositories and storage adapters;
- identity, consent and authorization;
- privacy and data classification;
- evidence and provenance;
- documents;
- authority and jurisdiction intelligence;
- submission and tracking;
- AI and Agentic AI;
- tools and skills;
- notifications;
- audit and observability;
- transport abstractions;
- decentralized providers;
- hardware/device evidence interfaces.

---

## 4. USER CHOICE: THE WORD OPTIONAL HAS A PRECISE MEANING

**Optional means optional for the user, not optional for the ecosystem.**

Janavani must provide the capability as part of the ecosystem where it is in scope. The citizen decides whether to invoke it, enable it, or share the information needed for that invocation.

Examples:

- AI is a permanent shared capability; the citizen may choose AI or a deterministic/non-AI path.
- Agentic AI is a shared capability; the citizen chooses whether to invoke it and consequential actions require policy and confirmation.
- Telegram is an access surface; a citizen may choose it, but Telegram is not the platform itself.
- Web3/decentralized features may be available; a citizen is not silently forced to use them.
- Cross-channel identity linking is user-controlled and explicit.

Safety, legal, device, destination, network and emergency constraints may limit a choice, but the limitation must be explicit.

---

## 5. AI AND AGENTIC AI

AI is a **shared Janavani capability fabric**, not the identity of Janavani and not a mandatory dependency for unrelated workflows.

Model/runtime families such as OCR, CV, SAM, VLM, SLM, LLM, MLM, MoE, LAM, RAG and Agentic AI are implementations or capability families. Providers are replaceable adapters.

A user may choose:

```text
AI assistance      -> yes
AI assistance      -> no
```

and both paths must remain valid.

Consent to use AI does not mean blanket permission to transmit personal or sensitive data. Data policy, capability scope, purpose and provider must be evaluated separately.

Agentic AI may research, explain, classify, draft, compare and prepare work. Consequential actions require scoped tool permission, policy evaluation, appropriate confirmation and provenance/audit.

AI must never fabricate authorities, laws, evidence, government actions, delivery acknowledgements or verification states.

---

## 6. PRIVACY AND DATA BOUNDARY

**Privacy by Design, Privacy by Default, Safety by Design and Safety by Default are ecosystem invariants.**

Personal and sensitive information remains under user/device control by default. Janavani must not become a central personal-data collection system merely because a capability exists.

Evidence originals remain local unless a specific, explicitly authorised operation requires transmission.

When transmission is genuinely required:

```text
Identify minimum required data
        |
        v
Minimise
        |
        v
Scrub unnecessary personal/sensitive data locally
        |
        v
Encode / structure
        |
        v
Encrypt
        |
        v
Explicit user-authorised operation
```

Encryption is not permission to collect. AI permission is not permission to transmit. Document generation is not permission to submit.

---

## 7. CASE IS THE CENTRAL CIVIC OBJECT

The canonical product object is the **Case**. A Case is the durable representation of a citizen's civic matter and its lifecycle.

The intended lifecycle is:

```text
Citizen Reality
 -> Understanding
 -> Structured Facts
 -> Evidence / Context
 -> Jurisdiction
 -> Responsible Authority
 -> Civic Action
 -> Document
 -> Citizen Review
 -> Explicit Approval
 -> Submission / Communication
 -> Acknowledgement
 -> Tracking
 -> Follow-up / Escalation
 -> Outcome
 -> Citizen Verification / Feedback
 -> Public Learning where appropriate
```

Different access surfaces must operate on the same Case model and lifecycle.

---

## 8. EVIDENCE AND PROVENANCE

Evidence, analysis and action are separate.

Evidence may include documents, photographs, video, audio, OCR output, timestamps, optional location, source references and integrity hashes.

Original evidence should remain local by default. Shared infrastructure may retain minimal references/metadata required for the workflow, subject to privacy policy.

Citizen reports, allegations, authoritative information, system-derived information, expert review, AI analysis and verified findings must remain distinguishable.

Provenance is shared infrastructure, not an Evidence-only feature. It may record creation, capture, import, transformation, hashing, review, sharing and deletion without storing attachment bytes in the provenance record.

---

## 9. AUTHORITY: CIVIC ISSUE -> RESPONSIBILITY -> ACTION

A citizen should not need to know the correct department, office, officer or legal label before using Janavani.

Janavani should progressively support:

```text
Citizen language
 -> Issue understanding
 -> Classification
 -> Location / jurisdiction
 -> Authority candidates
 -> Authoritative verification
 -> Responsible authority
 -> Action-path recommendation
```

Janavani must not guess authority information. Ambiguity must be represented as ambiguity and resolved using verified sources and required context.

---

## 10. DOCUMENTS ARE SEPARATE FROM SUBMISSION

Document generation and document submission are distinct capabilities.

The standard document flow is:

```text
Case + Authority + Evidence/Context
        |
        v
Draft
        |
        v
Citizen review / correction
        |
        v
Final document
        |
        +--> PDF
        +--> Editable document (for supported formats)
        |
        v
Print / download / submission instructions
```

Janavani must not silently email generated documents to an authority.

Any future electronic submission is a separate capability with its own destination, data, authorization, delivery, acknowledgement and audit contract.

---

## 11. LOCAL-FIRST STORAGE

Private Case/Evidence data should be local-first where the capability permits it.

The target browser pattern is:

```text
Device Key Provider
        |
        v
Web Crypto
        |
        v
Encrypted Local Vault
        |
        v
IndexedDB / equivalent local store
        |
        v
Provider-neutral Case/Evidence repositories
```

There is no implicit remote fallback for private data.

A recovery mechanism must be user-controlled and must not rely on a Janavani-held master key or raw passphrase.

---

## 12. RUST / PYTHON / WEB TECHNOLOGY DIRECTION

Rust is the canonical long-term domain/core direction.

This does **not** require a risky full rewrite today.

Preferred migration posture:

```text
Rust canonical domain/core
        |
        +--> Web/WASM/Dioxus clients
        +--> application/service bindings
        +--> future shared components

Python remains useful at integration/application edges
        |
        +--> Telegram / messaging
        +--> AI/RAG/provider integrations
        +--> transitional application services
```

Stable contracts come before language migration. Existing useful Python implementations should be converged behind canonical contracts rather than discarded merely because Rust is the long-term direction.

The Dynamic Web may be hybrid: public/discovery web can remain HTML/CSS/JS, while the rich citizen WebApp can use Rust/Dioxus/WASM. This is one ecosystem, not separate products.

---

## 13. PROVIDER NEUTRALITY

Technologies are providers/adapters, not domain authorities.

Examples include:

- PostgreSQL / Supabase / other storage;
- Ollama / cloud AI / future AI providers;
- Freenet / Nostr / IPFS / Nym / Reticulum / blockchain;
- messaging platforms;
- government APIs;
- future hardware and sensor systems.

A new provider should implement an existing capability contract where possible:

```text
New technology
 -> Adapter
 -> Stable capability contract
 -> Policy / health / tests
 -> Registry
 -> Available to compatible surfaces
```

Ollama is therefore a candidate local-AI provider, not the Janavani AI architecture. OpenClaw is a reference for agent/gateway/plugin design patterns, not a specification for Janavani.

---

## 14. HARDWARE AND FUTURE EVIDENCE CAPTURE

Hardware/device evidence capture is a future shared capability area, not a reason to create a hardware-specific application.

Potential inputs include camera, GPS, inertial sensors, documents, audio and other lawful device data. Any hardware implementation must preserve the same evidence, privacy, provenance and user-control contracts.

Mojo is research/watchlist material unless measured requirements justify it. It is not currently a canonical Janavani language.

---

## 15. RESEARCH RULE

External products, government grievance systems, civic applications, AI frameworks and open-source projects are **research inputs**.

We may learn from them, reuse compatible open-source components, or integrate external systems where justified. We do not copy their product boundaries or let them dictate Janavani architecture.

A useful external pattern should be expressed as a Janavani capability/contract and independently evaluated for privacy, security, reliability, legal fit, maintainability and citizen benefit.

---

## 16. CANONICAL EXECUTION / PROVENANCE ENVELOPE

The next foundational architecture primitive is a provider-neutral execution context for shared capabilities.

A capability invocation should eventually carry enough context to answer:

```text
Who initiated it?
Which capability?
Which operation?
Which Case/resource?
Which surface?
Which provider?
Which authorization/consent?
Which data class/purpose?
Which inputs/evidence?
What result/change occurred?
Was it deterministic, AI-assisted or human-reviewed?
What provenance/audit exists?
Can it be retried safely?
```

This should be implemented as shared infrastructure rather than separately inside each capability. A candidate decomposition is:

- `CapabilityExecutionContext`
- `OperationRecord`
- `ProvenanceRecord`

Status: **DESIGN DIRECTION — implementation not yet claimed**.

---

## 17. DOCUMENTATION AND REPOSITORY DISCIPLINE

Before adding a new Markdown file:

1. Read `docs/DOCUMENTATION_INDEX.md`.
2. Check the authority hierarchy.
3. Search for existing documents covering the same responsibility.
4. Extend an existing canonical document if appropriate.
5. Create a new document only when it has a distinct owner/purpose.
6. Record status and authority.
7. Update the index.

Before changing code:

1. Check the canonical architecture and task register.
2. Search for existing implementations.
3. Identify the canonical owner.
4. Preserve useful historical work.
5. Make the smallest justified change.
6. Test and verify.
7. Update documentation/evidence.

Archive first. Delete only after dependency, replacement, runtime and historical-value evidence.

---

## 18. COMPLETION DISCIPLINE

Never equate a file, class, endpoint or document with completion.

Use:

`VISION -> DESIGNED -> IMPLEMENTED -> FUNCTIONAL -> TESTED -> SECURITY-VERIFIED -> PRIVACY-VERIFIED -> FAILURE-ISOLATED -> PRODUCTION-READY`

The repository must distinguish architecture/design evidence from runtime/production evidence.

---

## 19. CURRENT EXECUTION FRONTIER — 11 SEPTEMBER 2026

The immediate work is:

1. Documentation/source-of-truth convergence.
2. Repository and runtime truth verification.
3. Canonical core/application contracts.
4. Identity, authorization, consent and policy enforcement.
5. Case + Evidence + Provenance + Authority + Document integration.
6. One complete deterministic civic-action vertical slice.
7. Dynamic Web/WebApp reference client.
8. Telegram convergence against shared contracts.
9. AI/Agentic AI production integration after deterministic workflow foundations are verified.
10. Expansion to additional surfaces and resilience/decentralized capabilities without creating parallel business logic.

Do not create another architectural generation merely because a new technology is interesting.

---

## 20. AI AGENT OPERATING RULE

An AI agent working on Janavani must:

- treat this document as orientation;
- obey `docs/DOCUMENTATION_INDEX.md` and the higher-authority documents;
- inspect the actual repository before claiming implementation;
- search before creating new files or abstractions;
- distinguish design from implementation and verification;
- avoid duplicate capabilities and duplicate documentation;
- preserve historical evidence through archive-first practice;
- never silently weaken privacy, consent, authorization, provenance or failure isolation;
- never make an interface-specific implementation the owner of shared business logic;
- report uncertainty and incomplete verification explicitly.

---

**END — JANAVANI AI / HUMAN / DEVELOPER CONTEXT**
