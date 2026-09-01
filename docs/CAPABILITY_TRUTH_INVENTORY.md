# Janavani Capability Truth Inventory

**Status:** Living audit register  
**Date:** 2026-08-26

## Purpose

This is the repository-wide register for deciding whether an advertised or implemented capability is real, partial, legacy, duplicated, unsafe, or unverified. It is an audit instrument, not a feature checklist.

## Evidence states

- **VERIFIED** — executable evidence proves the claimed behavior at the stated boundary.
- **PARTIALLY VERIFIED** — some behavior is proven but material paths remain unverified.
- **CONFIGURED** — configuration exists but execution is not proven.
- **UNVERIFIED** — implementation/claim exists without sufficient executable evidence.
- **FAILED** — applicable verification currently fails.
- **BLOCKED** — verification cannot proceed because a prerequisite is broken.
- **LEGACY** — implementation exists outside the canonical runtime and is retained for evidence/reference.
- **INVALID** — implementation falsely reports capability or otherwise cannot be treated as capability evidence.

## Current baseline

| Capability | Current evidence | Status | Immediate action |
|---|---|---|---|
| Canonical FastAPI runtime | `src.web.canonical_app:app` exists and is the intended runtime authority | PARTIALLY VERIFIED | complete deployment/runtime evidence |
| Storage abstraction | provider-neutral adapter exists | PARTIALLY VERIFIED | trace all direct provider consumers |
| Document rendering | canonical renderers exist | PARTIALLY VERIFIED | verify all active consumers |
| Civic complaint capability | shared capability contract/implementation exists | PARTIALLY VERIFIED | expand integration/failure tests |
| AI legal drafting | bounded implementation + degraded fallback exists | PARTIALLY VERIFIED | verify provider-independent behavior |
| Local SLM | prompt/test surface exists | FAILED | fix prompt contract; do not weaken test |
| Nostr | legacy publisher exists; canonical adapter not verified | UNVERIFIED / LEGACY | build shared real adapter |
| Nym | fake driver removed; real adapter not verified | UNVERIFIED | implement real transport adapter |
| Reticulum | fake driver removed; real adapter not verified | UNVERIFIED | implement real transport adapter |
| Freenet | research/design material exists; canonical integration not verified | UNVERIFIED | build Contract/Delegate/UI lab |
| Blockchain/ZKP | previous fake implementation removed | UNVERIFIED | implement actual verification/anchoring boundary |
| Cryptographic event verification | current code performs structural checks only | PARTIALLY VERIFIED | implement real cryptographic verification |
| SOS/emergency routing | implementation exists but delivery/wipe claims require safety audit | UNVERIFIED | define safety contract and delivery semantics |
| Android | repository architecture/claims require implementation evidence audit | UNVERIFIED | inspect canonical client implementation |
| iOS | repository architecture/claims require implementation evidence audit | UNVERIFIED | inspect canonical client implementation |
| DApp | repository architecture/claims require implementation evidence audit | UNVERIFIED | inspect canonical client implementation |
| Telegram | adapters exist across generations; canonical runtime ownership requires audit | UNVERIFIED | trace active adapter and integration tests |
| WhatsApp | capability is planned/claimed; canonical production evidence requires audit | UNVERIFIED | inspect implementation and provider evidence |
| Messenger | capability is planned/claimed; canonical production evidence requires audit | UNVERIFIED | inspect implementation and provider evidence |

## Rules for updating this inventory

1. A file existing is not evidence that a capability is operational.
2. A feature flag is not evidence that a capability is implemented.
3. A mock proves only the boundary behavior it is designed to test.
4. A provider diagnostic proves provider reachability/configuration only.
5. Configuration or credentials do not prove integration.
6. A `2xx` response does not prove business-level delivery or completion.
7. A generated identifier does not prove that a decentralized protocol accepted an operation.
8. A hash/signature length check does not prove cryptographic verification.
9. A client UI does not prove backend capability availability.
10. A documented roadmap item does not prove implementation.

## Multi-generation rule

For every duplicate implementation candidate, record:

- capability provided;
- generation/path;
- imports/consumers;
- runtime reachability;
- tests;
- replacement candidate;
- behavioral parity evidence;
- archival decision.

Do not archive or delete merely because a path contains `v2`, `v3`, `legacy`, `old`, or similar naming. Age is an investigation signal, not deletion evidence.

## Safety-critical rule

Safety-critical code such as SOS/emergency routing must not be refactored solely for architectural cleanliness. First establish its contract, threat model, delivery semantics, failure modes, user-facing guarantees, and test evidence.

## No-fake-green rule

When a real implementation is absent, the repository must expose `UNVERIFIED`, `FAILED`, `BLOCKED`, or an explicit unavailable/degraded state as appropriate. Do not replace missing capability with synthetic success to make tests or CI green.

## Required documentation coupling

When a capability moves to a new evidence state, update this inventory and the relevant architecture/capability document in the same change set. New implementations must add their verification evidence and failure-isolation behavior to documentation.
