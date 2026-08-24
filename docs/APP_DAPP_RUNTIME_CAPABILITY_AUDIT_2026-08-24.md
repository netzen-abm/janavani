# JANAVANI — APP + DAPP RUNTIME / CAPABILITY AUDIT

**Status:** ACTIVE — P0/P1 CONVERGENCE WORK
**Date:** 24 August 2026
**Purpose:** Establish evidence-based ownership before code migration, archival or deletion.

## 1. Decision

Janavani is being built as a full ecosystem, with **Android App + iOS App + DApp** as the first product-building focus.

The first-build priority does **not** reduce the ecosystem scope. Dynamic Web/WebApp, Telegram, Telegram Mini App, WhatsApp, Messenger, Nostr, Nym Mixnet, Reticulum Mesh, Freenet, blockchain/ZKP, AI/ML capabilities and future protocol adapters remain independent ecosystem capabilities.

A capability may be unavailable, degraded, disabled or refused without preventing unrelated capabilities from operating.

## 2. Non-negotiable runtime boundary

```text
                         JANAVANI CAPABILITY CONTRACTS
                                    |
       +----------------------------+----------------------------+
       |                            |                            |
   ANDROID APP                  iOS APP                       DAPP
       |                            |                            |
       +----------------------------+----------------------------+
                                    |
                         independent adapters
                                    |
       +-----------+-----------+----+----+-----------+------------+
       |           |           |         |           |            |
     Web/WebApp Telegram   WhatsApp  Messenger   CLI/Other    Future
       |           |           |         |       surfaces     adapters
       +-----------+-----------+---------+-----------------------+
                                    |
                         capability/transport policy
                                    |
       +----------+----------+----------+----------+--------------+
       |          |          |          |          |              |
     Internet   Nostr      Nym      Reticulum  Freenet       Blockchain/ZKP
       |          |          |          |          |              |
       +----------+----------+----------+----------+--------------+
                                    |
                              AI capability layer
                                    |
   OCR / CV / SAM / VLM / SLM / LLM / MLM / MoE / RAG / LAM / Agentic AI
```

No arrow in this diagram is a mandatory runtime dependency. Contracts define capability semantics; adapters provide optional implementations.

## 3. Evidence-backed current state

### 3.1 Canonical API assembly

`src/web/canonical_app.py` is the current canonical API assembly candidate. Existing verification tests establish canonical imports, platform endpoints and domain route prefixes. The repository must continue treating this assembly as the API authority unless a later evidence-based decision changes it.

### 3.2 Canonical client candidate

`src/web_dioxus/` is the current root Dioxus client candidate. However, `src/web_dioxus/src/main.rs` currently contains multiple concatenated implementations of `main`/`App`, including different protocol and storage variants. This is a **P0 structural defect**, not a reason to delete the client.

Action: reduce the file to one authoritative entry point and move capabilities into explicit modules/components.

### 3.3 Parallel generations

`janavani_v2/` and `janavani_v3/` remain historical/parallel workspaces. They must not be deleted until each useful capability is mapped to the canonical architecture and migration evidence exists.

### 3.4 Deployment authority

Deployment files require a separate authority audit. The root Docker configuration previously showed multiple concatenated implementations and an entrypoint that differed from the canonical FastAPI assembly. This must be corrected before production deployment is considered canonical.

### 3.5 Existing tests

The repository has a working Python regression suite. The latest local evidence recorded in the project conversation is **29 passed, 2 warnings** after synchronization with `origin/main`.

This proves the current Python test suite passes; it does **not** prove Android, iOS, DApp/WebAssembly, protocol adapters or AI capabilities are production-ready.

## 4. Capability ownership matrix

| Capability | First-class? | Independent? | Canonical contract needed | Current action |
|---|---:|---:|---:|---|
| Android App | YES | YES | YES | BUILD FIRST |
| iOS App | YES | YES | YES | BUILD FIRST |
| DApp/Web3 | YES | YES | YES | BUILD FIRST |
| Dynamic Web/WebApp | YES | YES | YES | BUILD IN PARALLEL, NOT DEPENDENCY |
| Telegram | YES | YES | YES | ADAPTER |
| Telegram Mini App | YES | YES | YES | ADAPTER |
| WhatsApp | YES | YES | YES | ADAPTER |
| Messenger | YES | YES | YES | ADAPTER |
| Nostr | YES | YES | YES | OPTIONAL TRANSPORT/IDENTITY/PROVENANCE |
| Nym Mixnet | YES | YES | YES | OPTIONAL PRIVACY TRANSPORT |
| Reticulum Mesh | YES | YES | YES | OPTIONAL RESILIENT TRANSPORT |
| Freenet | YES | YES | YES | OPTIONAL DECENTRALIZED PLATFORM/TRANSPORT |
| Blockchain | YES | YES | YES | OPTIONAL PROVENANCE/COORDINATION |
| ZKP | YES | YES | YES | OPTIONAL PRIVACY-PRESERVING PROOF |
| OCR | YES | YES | YES | OPTIONAL EVIDENCE INPUT |
| Computer Vision | YES | YES | YES | OPTIONAL EVIDENCE ANALYSIS |
| SAM | YES | YES | YES | OPTIONAL VISION SEGMENTATION |
| VLM | YES | YES | YES | OPTIONAL MULTIMODAL REASONING |
| SLM | YES | YES | YES | OPTIONAL LOCAL AI |
| LLM | YES | YES | YES | OPTIONAL LANGUAGE REASONING |
| MLM | YES | YES | YES | OPTIONAL LANGUAGE/MULTILINGUAL MODEL |
| MoE | YES | YES | YES | OPTIONAL MODEL ROUTING |
| RAG | YES | YES | YES | OPTIONAL SOURCE-GROUNDED KNOWLEDGE |
| LAM | YES | YES | YES | OPTIONAL ACTION/LOCAL AGENT CAPABILITY |
| Agentic AI | YES | YES | YES | OPTIONAL, HUMAN-APPROVAL GATED |
| Document generation | YES | YES | YES | CORE CIVIC CAPABILITY |
| Evidence/provenance | YES | YES | YES | CORE CIVIC CAPABILITY |
| Government information | YES | YES | YES | CORE CIVIC CAPABILITY |
| Bill/Act/Ordinance tracking | YES | YES | YES | CORE CIVIC CAPABILITY |
| Constitutional evaluation | YES | YES | YES | CORE CIVIC CAPABILITY |
| Grievance/complaint | YES | YES | YES | CORE CIVIC CAPABILITY |
| RTI/BSA workflows | YES | YES | YES | CORE CIVIC CAPABILITY |
| Service/office/officer reviews | YES | YES | YES | CORE CIVIC CAPABILITY |
| Officer accountability/escalation | YES | YES | YES | CORE CIVIC CAPABILITY |
| Government scheme/event discovery | YES | YES | YES | CORE CIVIC CAPABILITY |
| Government claim verification | YES | YES | YES | CORE CIVIC CAPABILITY |
| Financial contribution engine | YES | YES | YES | CORE CAPABILITY; TRANSPARENCY REQUIRED |
| SOS/emergency | YES | YES | YES | CORE SAFETY CAPABILITY |

## 5. Independence contract

Every capability adapter MUST expose explicit states equivalent to:

```text
AVAILABLE
DEGRADED
DISABLED_BY_USER
DISABLED_BY_POLICY
UNAVAILABLE
FAILED
NOT_CONFIGURED
```

A failure in one adapter must not be represented as a failure of Janavani as a whole.

Examples:

- AI unavailable -> manual civic workflow remains usable.
- OCR unavailable -> manual evidence entry remains usable.
- Blockchain unavailable -> ordinary civic case remains usable.
- Wallet unavailable -> no-wallet DApp mode remains usable where appropriate.
- Nostr unavailable -> another selected transport may operate.
- Nym unavailable -> another privacy transport may operate subject to policy.
- Reticulum unavailable -> Internet or another selected transport may operate.
- Freenet unavailable -> ordinary app/DApp workflows remain available.
- Telegram unavailable -> App/DApp case state remains authoritative.
- WhatsApp unavailable -> App/DApp case state remains authoritative.
- Android unavailable -> iOS/DApp/Web remain independent.
- iOS unavailable -> Android/DApp/Web remain independent.

## 6. User capability selection

The ecosystem contains the capabilities; the user chooses which capabilities to activate where technically appropriate.

Required UX properties:

- capability discovery;
- plain-language explanation;
- privacy impact explanation;
- network/transport explanation;
- data-retention explanation;
- cost/fee explanation;
- permission explanation;
- enable/disable controls;
- health/degraded state;
- no silent activation of wallet, blockchain transaction, external AI or high-impact agent action.

The system must distinguish **capability availability** from **capability activation**.

## 7. Core civic capability model

The first product should converge on a reusable civic case lifecycle:

```text
DISCOVER
  -> UNDERSTAND
  -> VERIFY
  -> IDENTIFY AUTHORITY
  -> PREPARE ACTION
  -> REVIEW
  -> USER APPROVAL
  -> SUBMIT / DELIVER
  -> TRACK
  -> RESPONSE
  -> ESCALATE / APPEAL / CLOSE
```

The lifecycle must support, as separate actions:

- complaint;
- grievance petition;
- RTI;
- BSA-related evidence/document workflow where relevant;
- citizen opinion/objection;
- policy response;
- bill/Act/ordinance opinion;
- officer/service review;
- government claim verification;
- scheme/event discovery;
- escalation to department head;
- administrative head escalation;
- relevant elected representative escalation;
- positive recognition/support for effective public service.

## 8. Constitutional and legal guardrails

Janavani may use constitutional principles and the stated governance framework as product and policy context, but software must not represent AI-generated constitutional/legal evaluation as authoritative legal advice.

Required distinction:

```text
SOURCE FACT
   -> ANALYSIS
   -> CONSTITUTIONAL / LEGAL REFERENCE
   -> POTENTIAL ISSUE / FLAG
   -> HUMAN REVIEW
   -> USER DECISION
```

The Golden Triangle and other constitutional principles should be represented through versioned, inspectable rules/references rather than hidden model behavior.

## 9. Financial contribution engine

The contribution capability must be independently usable and must not become a prerequisite for civic workflows.

Minimum contract requirements:

- purpose of contribution;
- recipient/beneficiary identity;
- amount and currency;
- fees;
- platform/operator charges if any;
- payment rail;
- transaction state;
- receipt/proof;
- refund/reversal state where applicable;
- public transparency fields where lawful;
- privacy controls for contributor identity;
- fraud/abuse controls;
- audit trail.

No blockchain requirement should be imposed merely because the contribution engine exists.

## 10. Documentation authority

The repository already defines an archive-first lifecycle and explicitly requires runtime, deployment and test verification before archival. fileciteturn902file0L2-L2

The App/DApp first-build plan explicitly establishes Android, iOS and DApp as independent peers over shared capability contracts and requires AI, blockchain and messaging failures not to block ordinary civic workflows. fileciteturn904file0L2-L2

Therefore this audit is subordinate to those governing documents and is intended to provide implementation evidence, not redefine the product constitution.

## 11. Immediate engineering sequence

### P0 — canonicalize without deleting

- [ ] Reduce `src/web_dioxus/src/main.rs` to one implementation.
- [ ] Enumerate all root Dioxus modules and their imports.
- [ ] Map v2/v3 Dioxus capabilities against root modules.
- [ ] Identify canonical mobile application roots.
- [ ] Identify canonical DApp/Web3 roots.
- [ ] Identify shared contract location.
- [ ] Identify storage boundaries.
- [ ] Identify transport adapters.
- [ ] Identify AI adapters.
- [ ] Identify evidence/document adapters.

### P1 — build the first independent vertical slice

- [ ] App shell.
- [ ] DApp shell.
- [ ] Capability selector.
- [ ] Civic case model.
- [ ] Local secure state.
- [ ] Evidence capture.
- [ ] Document generation.
- [ ] Review/approval.
- [ ] Submission abstraction.
- [ ] Tracking abstraction.
- [ ] Offline/degraded state.

### P1 — failure isolation

- [ ] Inject AI failure.
- [ ] Inject transport failure.
- [ ] Inject wallet failure.
- [ ] Inject blockchain failure.
- [ ] Inject OCR failure.
- [ ] Inject messaging failure.
- [ ] Inject remote API failure.
- [ ] Verify manual fallback.
- [ ] Verify case-state integrity.

## 12. Archive rule for this audit

No programming directory is to be archived solely because a newer-looking directory exists.

A directory becomes archive-eligible only after:

1. capability inventory;
2. import/reference inventory;
3. build/deployment inventory;
4. test inventory;
5. migration or replacement evidence;
6. archive manifest;
7. regression verification.

## 13. Current priority conclusion

**Build App + DApp first. Clean the architecture while building. Do not create a monolithic dependency graph. Do not delete v2/v3 prematurely.**

The most urgent implementation cleanup is the canonical Dioxus entry point and the explicit capability/adapter boundary. Once that is established, useful v2/v3 capabilities can be migrated selectively and the remainder archived in small auditable batches.
