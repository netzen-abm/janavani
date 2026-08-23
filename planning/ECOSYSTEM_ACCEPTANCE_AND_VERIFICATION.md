# JANAVANI — ECOSYSTEM ACCEPTANCE & VERIFICATION

**Status:** ACTIVE
**Version:** 2.0
**Date:** 23 August 2026

This document defines how Janavani capabilities are verified as part of the full ecosystem. It is not an MVP acceptance test.

## 1. Capability verification states

A capability progresses through:

`VISION → DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → PRODUCTION-READY`

A capability may remain at an earlier state while other ecosystem work proceeds.

## 2. Shared platform checks

- Capability has a clear owner.
- Capability has a documented contract.
- Capability does not depend on a presentation channel.
- Capability has defined data and permission requirements.
- Capability has defined AI/non-AI behavior where relevant.
- Capability has defined failure/fallback behavior.
- Tests exist at the appropriate level.

## 3. Interface checks

For every interface:

- Independent runtime boundary is defined.
- Interface consumes shared capabilities.
- Interface does not own shared business logic.
- Interface does not depend on another interface.
- Authentication/consent behavior is documented.
- Error and offline behavior are defined where relevant.

## 4. Web

Verify dynamic Web workflows against shared platform contracts, including citizen workflows, government information, documents, evidence, tracking, feedback, and governance views as capabilities become available.

## 5. Android / iOS

Verify independent application behavior, API contracts, local state, notifications, evidence capture, low-bandwidth/offline behavior where required, and privacy controls.

## 6. Telegram Bot / Mini App

Verify bot and Mini App as independent access surfaces. Existing Telegram workflow evidence is retained as a foundation, not treated as the scope boundary of Janavani.

## 7. WhatsApp / Messenger

Verify webhook/integration boundaries, identity/consent, capability routing, error handling, and interface independence.

## 8. API

Verify authentication, authorization, schemas, versioning, capability ownership, provenance, rate controls, and consumer isolation.

## 9. DApp / Web3

Verify cryptographic/provenance requirements, user control, key/identity safety, chain/storage dependencies, fallback behavior, and regulatory/operational constraints before production use.

## 10. AI

Verify source grounding, structured outputs, confidence/uncertainty, hallucination resistance, human approval gates, provider failure fallback, and separation of AI suggestions from authoritative facts.

## 11. Privacy and security

For applicable capabilities verify data minimization, consent, access control, retention, evidence protection, auditability, threat model coverage, abuse controls, and secure failure behavior.

## 12. Ecosystem acceptance

The ecosystem is not accepted because one interface works. Acceptance is continuous and capability-based. A capability is promoted only when its evidence satisfies the required verification state and the Master Task Checklist records the evidence.

## 13. Evidence sources

Preferred evidence sources are:

1. Actual GitHub implementation
2. Automated tests / CI
3. Runtime verification
4. Security/privacy verification
5. Architecture/contracts
6. Documentation

Documentation describes intent; implementation and verification establish actual status.
