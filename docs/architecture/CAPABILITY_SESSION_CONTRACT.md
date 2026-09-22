# Capability Session Contract

**Status:** IMPLEMENTED — canonical lifecycle kernel added; runtime/platform verification remains open

## Purpose

A Capability Session binds one temporary sensitive-resource use to one identity, one declared purpose, and one explicit lifecycle. It is the reusable infrastructure contract beneath camera, microphone, location, contacts, files, sensors, and similar capabilities.

## Canonical lifecycle

`NOT_REQUESTED → PURPOSE_PRESENTED → GRANTED → ACTIVE → PURPOSE_COMPLETE → RELEASED`

Exceptional pre-activation states are `DENIED` and `UNAVAILABLE`.

A released session is terminal. Later use requires a new session and a new purpose declaration.

## Required invariants

1. Every session has an opaque session ID.
2. Every session is bound to one canonical principal ID.
3. Every session names exactly one declared purpose and resource.
4. Surface adapters may implement platform mechanics but cannot weaken the lifecycle.
5. Activation requires the session's owning identity.
6. Purpose completion triggers data-minimisation hooks where configured.
7. Release triggers the platform resource-release hook where configured.
8. A released session cannot be reactivated.
9. OS permission revocation is attempted only where the platform permits it; application-level release is mandatory regardless.
10. Permission to access a resource does not imply permission for remote transmission, AI processing, biometric processing, or secondary use.
11. Sensitive logs must contain lifecycle metadata, not unnecessary sensitive payloads.

## Adapter contract

A surface adapter is responsible for translating this policy into its platform APIs. The shared contract remains responsible for identity binding, purpose binding, lifecycle state, release, and minimisation hooks.

## Security boundary

The session is not an authorization substitute. The execution path remains:

`Identity → Authorization → Purpose-Bound Session → Capability → Data/Resource`

Consequential external actions additionally require the canonical execution-context, consent, approval, idempotency, and submission gates.

## Verification

The canonical application-level lifecycle kernel is implemented in `src/access/capability_session.py` with regression coverage in `tests/test_capability_session.py` for purpose presentation, grant/activation, purpose completion, release, terminal-state enforcement, denied/unavailable terminal states, and invalid transitions.

Production readiness still requires platform-adapter tests for purpose declaration, refusal/fallback, identity isolation, activation, purpose completion, minimisation, release, OS permission-revocation limitations, and absence of unintended background access.
