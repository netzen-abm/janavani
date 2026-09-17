# Janavani SOS Safety/Privacy/Consequential Composition Contract

**Status:** Proposed integration contract  
**Scope:** Composition of the canonical SOS, Safety/Privacy, Authorization, Consent, and Consequential Operation boundaries

## 1. Purpose

This document defines how SOS composes existing control-plane primitives without introducing an SOS-specific policy or approval engine.

The canonical components remain separate:

- Authorization answers whether an identity may invoke a capability.
- Safety/Privacy answers whether the requested sensitive operation is permissible for its declared purpose and data scope.
- Consequential Operation Gate answers whether consent, execution context, and explicit approval permit an external side effect.
- SOS orchestrates the result and must never upgrade a weaker decision into a stronger one.

## 2. Canonical decision sequence

For a non-consequential SOS operation:

`Authorization → Safety/Privacy → SOS orchestration → optional delivery`

For a consequential SOS operation:

`Authorization → Safety/Privacy → Consequential Operation Gate → explicit approval/consent → SOS orchestration → verified delivery adapter`

The consequential gate is the canonical owner of approval semantics. SOS must not independently interpret `REQUIRE_APPROVAL` as approval, and Safety/Privacy must not grant an external side effect merely because sensitive access is allowed.

## 3. Approval semantics

The following states are distinct:

- **DENY / BLOCK:** terminal for the current operation.
- **REVIEW:** a further control-plane step is required; execution must not proceed.
- **REQUIRE_APPROVAL:** the consequential gate requires explicit user approval; execution must not proceed until that approval is supplied.
- **ALLOW:** all applicable control-plane checks have passed for the current execution context.

Approval is an input to a subsequent evaluation, not a mutable flag that a capability may set internally after receiving a review decision.

## 4. Execution context

Consequential SOS operations must carry the existing `CapabilityExecutionContext`, including:

- authenticated identity;
- capability and action;
- surface;
- resource/request identifier;
- risk level;
- external side-effect classification;
- idempotency key;
- authorization/consent/policy references where available.

The context is the shared audit and policy envelope. Do not create an SOS-specific execution-context model.

## 5. Consent and approval

If a consent requirement exists, the canonical consequential gate checks it. Explicit approval is separately evaluated. Having consent does not imply approval, and approval does not substitute for required consent.

For external high-risk side effects, an idempotency key is mandatory under the existing execution contract.

## 6. Safety/Privacy composition

Safety/Privacy remains responsible for purpose-bound sensitive access and transmission conditions. In particular:

- no explicit user choice → `BLOCK`;
- background/continuous sensitive access → `BLOCK`;
- remote transmission without an explicit transmission purpose → `BLOCK`;
- biometric processing must remain separately scoped;
- consequential action must use the external-action control path;
- non-minimized data requests → `MINIMIZE`.

Safety/Privacy does not itself perform transport, upload, police submission, or device permission operations.

## 7. SOS behavior

SOS may orchestrate only after the required gates permit the current operation.

A local-only SOS can proceed without a transport provider. Remote transmission requires the applicable Safety/Privacy decision and a destination. A consequential external action additionally requires the consequential-operation gate to return `ALLOW` for the exact execution context.

Delivery state remains truthful. Provider acceptance is not delivery, and an unknown provider outcome remains `UNKNOWN`.

## 8. No policy duplication

The integration must not add:

- an SOS approval enum that replaces `ConsequentialDecision`;
- an SOS consent repository;
- a second authorization evaluator;
- a second purpose-bound permission lifecycle;
- a second sensitive-data policy engine;
- provider-specific policy decisions inside SOS.

Thin translation code is permitted where one canonical request model must be mapped into another. Such translation must preserve identity, purpose, resource, risk, side-effect, consent, approval, and provenance semantics.

## 9. Approval retry model

A review-required consequential request should return a non-executing decision to the surface. The surface may then obtain explicit approval from the user and submit a new evaluation carrying that approval in the canonical consequential-operation request.

The original operation must not be executed between the two evaluations merely because a prior evaluation produced `REVIEW` or `REQUIRE_APPROVAL`.

## 10. Failure behavior

If any hard control denies the operation, later layers cannot override it. If approval is required but absent, no external action occurs. If a transport is unavailable, SOS may preserve a local result or queue according to the transport contract, but must not claim successful delivery.

## 11. Integration tests

The integration test suite must prove:

1. authorized non-consequential SOS can reach the SOS orchestration path;
2. unauthorized identity is denied;
3. Safety/Privacy `BLOCK` prevents SOS execution;
4. Safety/Privacy `REVIEW` prevents execution;
5. consequential SOS without explicit approval does not call a delivery adapter;
6. consequential SOS with matching consent and explicit approval reaches the delivery adapter;
7. authorization denial remains terminal even when consent and approval are present;
8. provider `ACCEPTED` remains `ACCEPTED` rather than `DELIVERED`;
9. provider acknowledgement produces `ACKNOWLEDGED`;
10. no provider or device implementation is constructed by the control-plane integration.

## 12. Implementation boundary

This integration contract does not implement HTTP, police control-room submission, camera/microphone/location permissions, biometric processing, Redis, Nostr, Reticulum, satellite, messaging, or storage providers.

Those remain separate adapters behind their canonical contracts.
