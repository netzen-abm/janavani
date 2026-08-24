# 🇮🇳 JANAVANI — APP + DAPP FIRST BUILD PLAN

**Status:** ACTIVE — FIRST PRODUCT BUILD PRIORITY  
**Date:** 24 August 2026  
**Scope:** Android, iOS and DApp/Web3, built as independent access surfaces over shared Janavani capability contracts.

## 1. Decision

The first product-building focus is **Janavani App + DApp**.

This does **not** change the full-ecosystem destination. It changes the implementation order so that the native mobile applications and DApp establish the first complete user-facing product surfaces while the Dynamic Web/WebApp, APIs, messaging and other interfaces continue as independent ecosystem surfaces.

The App and DApp are peers. Neither may become a runtime dependency of the other.

## 2. Product surfaces

### Mobile App

- Android application
- iOS application
- Shared mobile design system where practical
- Platform-specific adapters where required
- Offline/low-bandwidth support where appropriate
- Secure local state
- Evidence capture
- Notifications
- Case tracking
- Optional location
- Personal SOS
- User-controlled capability selection
- Optional local AI

### DApp

- Independent browser/Web3 application
- Wallet connection only when the user chooses a Web3 capability
- No-wallet mode for ordinary civic capabilities where technically appropriate
- Verifiable credentials/provenance where justified
- Optional decentralized evidence anchoring
- Optional decentralized identity
- Optional decentralized storage/transport
- Transparent network/transaction state
- No blockchain requirement for ordinary civic or SOS workflows

## 3. Shared platform boundary

Both App and DApp consume shared contracts:

```text
             JANAVANI CAPABILITY CONTRACTS
                        │
          ┌─────────────┴─────────────┐
          │                           │
      MOBILE ADAPTER              DAPP ADAPTER
          │                           │
     Android / iOS               Browser / Web3
```

Shared contracts may include:

- authentication and session contracts;
- consent and authorization;
- capability discovery;
- civic case lifecycle;
- document generation;
- evidence/provenance;
- government information;
- submission/tracking;
- notification/delivery state;
- privacy controls;
- security/audit;
- AI capability routing;
- health/degraded-state contracts.

Presentation, local storage, wallet integration and device APIs remain surface-specific.

## 4. First App vertical slice

The first production-oriented App slice should be:

`onboard → choose capability → describe issue → understand → identify authority → prepare action → capture/attach evidence → review → approve → submit → track`

The workflow must function without AI where practical.

AI can improve the workflow but cannot own the workflow.

## 5. First DApp vertical slice

The first DApp slice should be:

`connect/use without wallet → choose Web3 capability → inspect provenance/credential/evidence state → user confirmation → perform optional decentralized action → verify transaction/state → return to ordinary civic lifecycle`

A Web3 action must be explicit, reversible where technically possible, and understandable to the user before confirmation.

## 6. Independence rules

- Mobile failure must not break DApp.
- DApp failure must not break mobile.
- Android failure must not break iOS.
- iOS failure must not break Android.
- Web failure must not break either.
- Blockchain failure must not break ordinary civic workflows.
- Wallet/provider failure must not break no-wallet workflows.
- AI failure must not prevent deterministic civic workflows.
- OCR/CV failure must leave manual evidence paths available.
- RAG failure must produce a truthful degraded state.
- Agent failure must leave a guided/manual workflow available.
- Messaging failure must not block App or DApp case state.

## 7. Privacy and safety

Privacy and safety are defaults, not optional add-ons.

Required controls include:

- minimum necessary collection;
- explicit consent;
- user-controlled identity linking;
- local secure storage where appropriate;
- no silent wallet connection;
- no silent blockchain transaction;
- transaction preview before signing;
- human confirmation for consequential external actions;
- provenance and verification status;
- retention controls;
- secure evidence handling;
- auditability;
- abuse/rate controls;
- truthful delivery and transaction states.

## 8. AI integration rule

The App and DApp do not embed one mandatory AI stack.

Capabilities may route to:

`OCR / CV / SAM / VLM / SLM / LLM / MLM / MoE / RAG / LAM / Agentic AI`

according to the capability contract, device, user preference, privacy mode, availability and policy.

The system must support:

- local AI where appropriate;
- remote AI where explicitly enabled/needed;
- deterministic fallback;
- provider/model replacement;
- source-grounded RAG;
- human approval for consequential agent actions.

## 9. DApp/Web3 rule

Web3 is a capability, not an identity requirement for Janavani.

Use decentralized technology only where it provides a concrete benefit such as verifiable provenance, user-controlled credentials, decentralized coordination or resilient infrastructure.

Do not put ordinary civic case state, emergency operation or critical service availability behind a blockchain consensus dependency unless a separately verified requirement explicitly justifies it.

## 10. Build sequence

1. Runtime and API authority verification.
2. Capability contracts and dependency boundaries.
3. App/DApp shared API contract.
4. Mobile shell and secure local state.
5. DApp shell and wallet/no-wallet boundary.
6. Capability selection and civic case model.
7. First App vertical slice.
8. First DApp vertical slice.
9. Evidence/provenance.
10. Submission/tracking.
11. Offline/degraded behavior.
12. AI capability adapters and fallbacks.
13. Security/privacy verification.
14. Failure-injection verification.
15. Android/iOS production hardening.
16. DApp/Web3 production hardening.

## 11. Definition of done

App + DApp first-build milestone is not complete because screens render.

It is complete when representative users can independently execute the first vertical slice on the App and DApp, with shared capabilities but independent runtime paths, while preserving privacy, safety, provenance, user choice, degraded operation and truthful state reporting.

**The App and DApp are the first product surfaces. The ecosystem remains the target.**
