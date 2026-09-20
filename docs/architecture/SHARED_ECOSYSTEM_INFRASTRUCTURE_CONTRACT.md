# Janavani Shared Infrastructure Contract

## Status

Canonical architecture rule for the Janavani ecosystem.

## Core rule

**Every reusable skill, capability, tool, resource, feature, policy, security control, provider contract, and domain service is shared infrastructure by default.**

A WebApp, Telegram Bot, Android app, iOS app, DApp, Mini App, WhatsApp adapter, Messenger adapter, AI service, or agent is an **access surface**, not a separate implementation of the underlying capability.

The default architecture is therefore:

```
Access Surface
      |
      v
Surface Adapter
      |
      v
Shared Capability Contract
      |
      +--> Authorization
      +--> Identity
      +--> Consent
      +--> Provenance
      +--> Policy
      +--> Provider Contract
      |
      v
Shared Infrastructure
      |
      v
Provider / Storage / External Adapter
```

## What must be shared

The following are ecosystem infrastructure unless an explicit architecture decision says otherwise:

- identity and identity-linking contracts
- authorization and policy evaluation
- capability execution envelopes
- consent and purpose/scope enforcement
- privacy and data-minimisation controls
- provenance and audit events
- Civic Case lifecycle
- Evidence registration and attachment
- Authority resolution
- Document generation contracts
- Document review
- consequential-action approval
- submission contracts
- repository/provider contracts
- transaction / unit-of-work contracts
- external-tool delegation contracts
- AI and agent capability boundaries
- permission and device-access contracts
- safety and fail-closed controls
- observability and verification contracts
- common schemas and serialization contracts
- research/evidence provider contracts

## What may remain surface-specific

Only the adapter layer should normally be surface-specific:

- Telegram update/handler mechanics
- HTTP routing and request models
- Android/iOS UI and lifecycle APIs
- WhatsApp/Messenger transport APIs
- DApp wallet/session mechanics
- browser/mobile permission prompts
- surface-specific presentation and interaction

Surface-specific code must translate into shared contracts. It must not create a competing Case, authorization, consent, evidence, document, or submission implementation.

## Independence rule

Surfaces remain independently deployable.

Failure of Telegram must not disable WebApp. Failure of WebApp must not disable Telegram.

Independence does **not** mean duplicated business logic.

It means:

```
Independent deployment
        +
shared capability infrastructure
        +
shared policy/security contracts
```

## Provider neutrality

Capabilities must depend on provider contracts, not directly on a specific database, cloud vendor, AI provider, storage provider, messaging provider, or research provider.

Provider selection belongs at composition/runtime boundaries.

## Identity rule

A surface identifier is not automatically the canonical citizen identity.

Examples:

- Telegram user ID
- WhatsApp number
- browser session ID
- device ID
- wallet address

must be treated as surface/provider identities until an explicit identity-linking/authentication process establishes a canonical principal.

## Permission rule

Device permissions are purpose-bound.

A surface requests access only for the declared purpose, uses the capability, and releases/disables the access when the purpose is complete where the platform permits such control. A later use requires a fresh valid permission state.

## Branch rule

The repository maintains exactly nine intentional long-lived branches.

Historical branches are temporary source material. Useful deltas are promoted to `main`; obsolete branches are closed and deleted.

No `v2`, `v3`, `final`, `clean`, or equivalent parallel generations are permitted as long-lived branches.

## Acceptance criterion

A capability is considered ecosystem-ready only when:

1. it has a provider-neutral contract;
2. authorization is enforced at the capability boundary;
3. consent is enforced where applicable;
4. provenance is preserved;
5. at least two independent access surfaces can consume it without duplicating its domain logic;
6. negative authorization paths are tested;
7. provider selection remains outside the access surface.

## Canonical product spine

```
Canonical Identity
      ↓
Case
      ↓
Evidence
      ↓
Authority
      ↓
Document
      ↓
Review
      ↓
Consent
      ↓
Consequential Action
      ↓
Submission
      ↓
Outcome
```

This spine is infrastructure. Individual surfaces are adapters over it.
