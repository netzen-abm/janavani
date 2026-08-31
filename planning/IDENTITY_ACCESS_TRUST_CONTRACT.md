# JANAVANI — IDENTITY, ACCESS & TRUST CONTRACT

**Status:** DESIGNED
**Version:** 1.0
**Date:** 31 August 2026

## 1. Purpose

This contract defines the shared Identity, Access and Trust boundary for Janavani. It is an ecosystem capability, not a Web-only, Telegram-only, or mobile-only implementation.

The contract separates:

- identity;
- authentication;
- authorization;
- capability permission;
- consent;
- destination authorization;
- session/device state;
- credential/token handling;
- audit and provenance;
- revocation and recovery.

No interface may invent its own incompatible identity or authorization model when consuming shared Janavani capabilities.

## 2. Core Principle

**Authentication is not identity. Identity is not authorization. Authorization is not consent. Consent is not delivery.**

A citizen may use Janavani without creating a persistent centralized identity where the selected capability does not require one.

## 3. Identity Modes

### Anonymous

No Janavani account identity is required. The capability may operate with locally generated ephemeral identifiers where technically necessary, provided they are not used to construct a persistent behavioural profile.

### Local identity

Identity information is held on the citizen device and used only for selected capabilities. Examples include name, address, phone and email when locally needed to prepare a document.

### Authenticated identity

A citizen or authorized actor may authenticate when a capability genuinely requires persistent account continuity, synchronization, recovery, delegated access, or another justified security property.

Authentication must not automatically grant access to unrelated capabilities.

### Cryptographic identity

Capabilities such as Nostr or Web3 may use locally controlled cryptographic keys. A private key is signing authority, not a general Janavani account password.

## 4. Authentication Methods

Authentication mechanisms are capability-specific and replaceable behind this contract. Supported mechanisms may include:

- device-bound/local authentication;
- passkeys/WebAuthn;
- OAuth/OIDC federation where justified;
- verified email or phone challenge where legally and operationally justified;
- cryptographic signatures for decentralized capabilities;
- service-to-service credentials for integrations.

Passwords should not be introduced unless there is a demonstrated requirement that cannot be met more safely by a modern passwordless mechanism.

## 5. Authorization

Every protected capability request must evaluate authorization independently of authentication.

Authorization decisions should consider:

```text
Principal
  + Capability
  + Action
  + Resource
  + Context
  + Policy
  + Consent state
  + Risk level
  → Allow / Deny / Require approval
```

Role-based access control may be used where appropriate, but sensitive citizen workflows should prefer least privilege and resource/capability-level policy over broad roles.

## 6. Capability Permissions

Each optional capability has its own permission boundary.

Examples:

- AI access;
- cloud processing;
- messaging submission;
- government submission;
- document generation;
- evidence processing;
- Web3 signing;
- decentralized publishing;
- synchronization.

Enabling one capability must not silently enable another.

## 7. Consent

Consent is explicit, purpose-bound and distinguishable from authentication.

Before sensitive transmission, the user should be able to understand:

1. what data will leave the device;
2. why it is required;
3. where it will go;
4. who will receive it;
5. expected retention;
6. whether the action is reversible;
7. whether the action has legal or consequential effects.

A successful authentication must never be treated as blanket consent for future transmissions.

## 8. Session and Device Model

Where authenticated sessions are implemented:

- sessions must be scoped to a principal and client/device;
- access tokens must be short-lived;
- refresh credentials must be protected and revocable;
- logout/revocation must invalidate future use;
- device/session lists should be available for persistent accounts where appropriate;
- high-risk actions may require step-up authentication or explicit user approval;
- tokens must not be written to ordinary logs.

For browser clients, prefer secure, HttpOnly, SameSite cookies for session credentials rather than exposing long-lived bearer tokens to application JavaScript where architecture permits.

## 9. Token Contract

Tokens must have explicit type, audience, issuer, expiry and scope semantics.

Minimum conceptual fields:

```text
issuer
subject
audience
issued_at
expires_at
scope / permissions
session_id
key_id where applicable
```

Do not accept a token merely because it is syntactically valid. Validate issuer, audience, signature, expiry, required scope, revocation state where applicable, and capability policy.

Never place access tokens or private credentials in URLs, source code, client bundles, telemetry, crash reports, or ordinary application logs.

## 10. Service Credentials

Infrastructure credentials such as Telegram bot tokens, AI-provider API keys, Supabase credentials and external integration secrets are service credentials, not citizen identity credentials.

They must:

- exist only in appropriate server/deployment secret stores or protected environments;
- never be committed to the repository;
- never be embedded in public client code;
- be scoped to the minimum required capability;
- be rotated when exposure is suspected;
- be excluded from logs and diagnostics.

## 11. Cryptographic Keys

Private keys used by decentralized capabilities remain under the control of the capability owner/user as appropriate.

Private keys must not be copied into unrelated central databases. Signing operations should expose the minimum transaction/payload context needed for user approval.

Key loss and recovery must be explicitly designed; Janavani must not imply recovery is possible when a cryptographic key has been irretrievably lost.

## 12. Request Flow

Canonical protected-request flow:

```text
Interface / Adapter
        ↓
Identity context
        ↓
Authentication verification (if required)
        ↓
Capability + action identification
        ↓
Authorization policy
        ↓
Consent / approval gate (if required)
        ↓
Data minimization + provenance checks
        ↓
Capability execution
        ↓
External destination (if selected)
        ↓
Outcome + audit/provenance record
```

A request must not proceed merely because a caller has authenticated.

## 13. External Destination Boundary

Government offices, messaging providers, AI providers, decentralized relays and blockchain networks are separate trust boundaries.

Authorization to use Janavani does not imply authorization to transmit to an external destination. Destination authorization must be evaluated as part of the selected capability.

An attempted transmission must never be represented as confirmed delivery without evidence from the destination.

## 14. Failure and Degraded Operation

Authentication infrastructure must not become a universal single point of failure.

If an identity service is unavailable, capabilities that can safely operate anonymously or locally should continue. Protected capabilities requiring verified identity must fail closed rather than silently downgrade security.

Interface failure must not revoke or disable unrelated interface capabilities.

## 15. Privacy Requirements

This contract inherits the Janavani privacy architecture:

- minimum necessary collection;
- local-first processing where practical;
- no central personal-data repository by default;
- no behavioural identity graph;
- encryption in transit;
- secure storage for sensitive local data;
- explicit transmission decisions;
- capability isolation;
- retention discipline.

## 16. Audit and Provenance

Security-relevant events may be recorded using minimized operational metadata. Logs must not become a shadow identity database.

Where a consequential action occurs, the system should preserve sufficient provenance to establish:

- which capability was invoked;
- which principal or anonymous context acted, where applicable;
- which policy decision was made;
- whether user approval was required and obtained;
- what destination was selected;
- whether execution was attempted, accepted, rejected or confirmed.

## 17. Security States

Identity/access capabilities use the repository's status discipline:

`VISION` → `DESIGNED` → `IMPLEMENTED` → `FUNCTIONAL` → `TESTED` → `SECURITY-VERIFIED` → `PRIVACY-VERIFIED` → `PRODUCTION-READY`

Documentation alone does not establish implementation or security verification.

## 18. Required Future Components

The implementation should converge toward these shared components:

```text
identity/
  principal
  identity-mode

auth/
  authenticators
  sessions
  tokens
  passkeys/federation adapters

access/
  policy
  authorization
  capability-permissions
  consent

trust/
  provenance
  audit
  external-destination authorization

security/
  secret handling
  key management
  revocation
  recovery
```

Exact code locations remain an implementation decision and must follow the canonical architecture rather than creating duplicate auth stacks in individual interfaces.

## 19. Non-Goals

This contract does not mandate:

- mandatory citizen registration;
- mandatory centralized identity;
- mandatory passwords;
- mandatory JWT;
- mandatory OAuth provider;
- mandatory blockchain identity;
- mandatory AI identity;
- mandatory synchronization;
- mandatory data retention.

The correct mechanism depends on the capability and threat model.

## 20. Acceptance Criteria

The Identity, Access & Trust capability is not production-ready until:

- identity modes are implemented and tested;
- protected requests have a common authorization boundary;
- service credentials are separated from citizen credentials;
- tokens/sessions have expiry and revocation semantics;
- high-risk actions have explicit approval gates;
- secrets are absent from client bundles and logs;
- authorization is tested for denial as well as success;
- cross-interface behaviour is verified;
- privacy review is complete;
- threat modelling is complete;
- security verification evidence is recorded;
- current documentation matches actual code and deployment.

## 21. Architectural Rule

**Janavani should authenticate only when authentication creates real value for the selected capability, authorize every protected action independently, obtain explicit approval for consequential transmission, and keep identity and cryptographic authority under citizen control wherever practical.**
