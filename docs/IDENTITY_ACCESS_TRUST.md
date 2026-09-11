# Janavani — Identity, Access & Trust

**Status:** DESIGNED / ACTIVE ARCHITECTURAL CONTRACT
**Version:** 2.0
**Date:** 11 September 2026

## Purpose

This document is the canonical active contract for Janavani's shared Identity, Access & Trust boundary. It consolidates the previously separate planning contract and implementation map without turning authentication into a mandatory account system.

Janavani is an ecosystem. Identity, authentication, authorization, capability permission, consent, destination authorization, session/device state, credentials, revocation, audit, and provenance are shared capabilities consumed by independent interfaces.

## Core distinction

> **Authentication is not identity. Identity is not authorization. Authorization is not consent. Consent is not delivery.**

A citizen may use Janavani anonymously or with local identity wherever the selected capability does not genuinely require persistent authentication.

## Identity modes

- **Anonymous:** no persistent Janavani identity where the capability does not require one.
- **Local identity:** identity data remains on the citizen device unless explicitly transmitted for a selected capability.
- **Authenticated identity:** persistent continuity, recovery, synchronization, delegation, or another justified security property requires authentication.
- **Cryptographic identity:** Nostr/Web3 capabilities may use device-controlled keys; these are capability credentials, not automatically universal Janavani identity.

Anonymous or local use must not be converted into a behavioural identity graph merely for convenience.

## Authentication

Authentication mechanisms are replaceable adapters behind the shared contract. Possible mechanisms include device-bound authentication, passkeys/WebAuthn, OAuth/OIDC federation where justified, verified contact challenges where justified, cryptographic signatures, and service-to-service credentials.

Do not introduce passwords or a generic JWT login merely because they are familiar. Select mechanisms according to the capability and threat model.

## Canonical authorization boundary

Every protected request must pass through a shared policy decision boundary:

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

Authorization must not be represented by a simple `authenticated == true` check.

The same boundary must serve Web, Telegram, mobile, messaging, API, DApp/Web3, AI, agentic AI, and future interfaces.

## Capability permissions

Each optional capability has its own permission boundary. Examples include AI processing, cloud processing, messaging transmission, government submission, document generation, evidence processing, Web3 signing, decentralized publishing, and synchronization.

Enabling one capability must not silently enable another.

## Consent and approval

Consent is explicit and purpose-bound. Before sensitive or consequential transmission, the citizen should understand, as applicable:

1. what data leaves the device;
2. why it is required;
3. where it goes;
4. who receives it;
5. expected retention;
6. whether it is reversible;
7. whether it creates legal or other consequential effects.

Authentication is never blanket consent.

High-risk actions require an appropriate approval gate, including external submission, public evidence publication, blockchain signing, external messaging, consequential agentic actions, and security/recovery changes.

## Session separation

Conversation/workflow state and authentication state are different domains.

```text
Workflow state:
  What is happening in this civic interaction?

Identity/access state:
  Who or what is requesting this action?
  How was it authenticated?
  What may it do?
  What approval exists?
```

Do not turn `conversation/session.py` into the authentication system. Workflow identity fields are not automatically persistent citizen profiles.

## Principal context

A normalized request context should conceptually carry:

```text
principal_id
identity_mode
interface
session_id (if authenticated)
authentication_method (if authenticated)
scopes
capabilities
consent_context
risk_context
```

Exact implementation structures must follow the actual repository architecture.

## Token and credential rules

Tokens, where needed, must have explicit issuer, subject, audience, issued-at, expiry, scope/permissions, session ID, and key ID semantics as applicable.

Validate signature, issuer, audience, expiry, required scope, and applicable revocation state. Do not accept credentials merely because they are syntactically valid.

Service credentials (for example messaging, database, AI-provider, or integration credentials) are not citizen credentials. They must remain in protected deployment/server configuration and never appear in client bundles, URLs, telemetry, crash reports, or ordinary logs.

Private cryptographic keys remain under the control of the relevant capability owner/user and must not be copied into unrelated central storage.

## External destination authorization

Government authorities, messaging providers, AI providers, decentralized relays, and blockchain networks are separate trust boundaries.

Authorization to use Janavani does not authorize transmission to an external destination. Destination authorization must be evaluated as part of the selected capability.

An attempted transmission is not a confirmed delivery. Confirmation requires destination evidence.

## Privacy boundary

This contract inherits the Janavani data-boundary rules:

- minimum necessary collection;
- local-first processing where practical;
- no central personal-data repository by default;
- explicit capability choice;
- minimized encrypted transfer;
- no hidden cross-capability replication;
- no unnecessary behavioural tracking;
- retention discipline;
- failure isolation.

## Cross-interface independence

Telegram authentication to the Telegram service is integration authentication, not citizen authentication. Each interface maps its channel context into the shared Janavani request context and then uses the same authorization boundary.

A failure of Telegram, Web, Android, iOS, WhatsApp, Messenger, DApp/Web3, or another optional capability must not disable unrelated capabilities.

## Failure behaviour

Use explicit states such as:

`available` · `unavailable` · `degraded` · `offline` · `permission_denied` · `user_disabled` · `configuration_required`

Protected capabilities fail closed when required authorization cannot be established. Capabilities that can safely operate locally or anonymously should not be disabled merely because an authentication service is unavailable.

## Audit and provenance

Security-relevant events may record minimized operational metadata. Logs must not become a shadow identity database.

For consequential actions, preserve sufficient provenance to establish:

- capability invoked;
- principal/anonymous context, where applicable;
- policy decision;
- approval/consent state;
- selected destination;
- attempted/accepted/rejected/confirmed outcome.

## Implementation boundary

The architectural boundary is shared, but implementation must be incremental and evidence-driven:

1. preserve current conversation behaviour;
2. introduce normalized principal/request context;
3. keep workflow sessions separate from identity/access state;
4. implement the canonical authorization/policy decision boundary;
5. add capability permissions and consent gates;
6. add authentication/session mechanisms only where justified;
7. adapt independent interfaces to the shared boundary;
8. verify denial, expiry, revocation, scope, consent, isolation, and failure paths.

Do not perform a broad authentication rewrite merely to create a fashionable stack.

## Completion standard

Identity/Access/Trust follows:

`VISION → DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → FAILURE-ISOLATED → PRODUCTION-READY`

Documentation is not implementation evidence.

## Non-goals

This contract does not mandate:

- mandatory citizen registration;
- centralized citizen identity;
- passwords;
- JWT;
- OAuth provider;
- blockchain identity;
- AI identity;
- synchronization;
- permanent data retention.

## Related documents

- `docs/SOURCE_OF_TRUTH.md`
- `docs/ARCHITECTURE_DATA_BOUNDARY.md`
- `docs/ARCHITECTURE.md`
- `docs/ARCHITECTURE_DECISIONS.md`
- `docs/AUTHENTICATION.md` — current implementation-state note
- `docs/90-audits/DOCUMENTATION_CONVERGENCE_REGISTER_2026-09-11.md`

## Architectural rule

**Authenticate only when authentication creates real value for the selected capability; authorize every protected action independently; obtain explicit approval for consequential transmission; and keep identity and cryptographic authority under citizen control wherever practical.**
