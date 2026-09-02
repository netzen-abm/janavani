# Canonical Janavani Identity Persistence Contract

**Status:** Contract / design boundary
**Version:** 1.0
**Scope:** Shared identity, authentication mapping, authorization preparation

## 1. Purpose

Janavani is a multi-surface civic ecosystem. Identity must therefore be independent of Telegram, Web, Android, iOS, WhatsApp, Messenger, DApp, or any individual authentication provider.

This contract defines the boundary between channel authentication, normalized Janavani identity, persistent identity records, authorization, and civic capabilities.

It does **not** implement an authentication provider, PostgreSQL schema, or RLS policy. Those require separate security and infrastructure verification.

## 2. Canonical flow

```text
Channel / Interface
        ↓
Provider Authentication
        ↓
External Identity Reference
        ↓
Janavani Identity Mapping
        ↓
Principal / IdentityContext
        ↓
Authorization Policy
        ↓
Capability
        ↓
Repository / Durable Storage
```

Authentication establishes who controls a credential or external account. Authorization determines what that principal may do. Consent remains a separate capability and legal-purpose boundary.

## 3. Canonical identity

The Janavani identity identifier MUST be an opaque, stable identifier generated and owned by Janavani.

It MUST NOT be derived directly from:

- phone number
- email address
- Telegram user/chat ID
- WhatsApp identifier
- OAuth/OIDC subject alone
- access token
- API key
- public-facing username

Provider identifiers may be retained as provider-specific identity mappings where necessary, subject to purpose limitation and privacy requirements.

## 4. Relationship model

```text
Janavani Identity
      │
      ├── External Identity Mapping(s)
      │       ├── Web/OIDC
      │       ├── Passkey
      │       ├── Telegram
      │       ├── WhatsApp
      │       └── other adapters
      │
      ├── Session(s)
      │
      ├── Consent Record(s)
      │
      └── Capability-owned records
              └── Civic Case(s)
```

One Janavani identity may have multiple external identity mappings. One external identity mapping MUST NOT silently create multiple Janavani identities without an explicit verified account-linking policy.

## 5. Principal mapping

The existing `src/identity` package is the runtime-neutral boundary.

Adapters resolve channel/provider information into `Principal` / `IdentityContext`. The principal carries an opaque `principal_id`, interface metadata, authentication method, session reference, scopes, and capabilities.

Provider-specific authentication logic MUST remain outside the identity domain model.

## 6. Authentication states

The implementation must distinguish at least:

- unauthenticated / anonymous
- locally identified but not remotely authenticated
- authenticated
- cryptographically authenticated where applicable
- authentication expired/revoked
- account disabled/revoked

An authenticated session MUST NOT be inferred merely because a channel supplied an identifier.

## 7. Authorization

Authorization is separate from authentication.

Minimum policy inputs:

- principal identity
- authentication assurance/method
- capability
- requested operation
- resource ownership or relationship
- case sensitivity/classification where applicable
- consent state where applicable
- administrative/service role where applicable

Authorization decisions MUST be enforced at the service/repository boundary and ultimately reflected in database authorization controls for durable data.

## 8. Case ownership

For Civic Case records:

```text
case.created_by → canonical Janavani identity
```

A channel identifier is metadata about the originating interface, not the canonical owner.

A case may be created anonymously only where the capability explicitly permits anonymous operation. Such cases MUST have a defined ownership/continuation policy before durable persistence and sensitive follow-up are enabled.

## 9. External identity mapping

A provider mapping should conceptually contain:

- mapping identifier
- Janavani identity identifier
- provider name
- provider subject/reference
- authentication method
- verification state
- created timestamp
- last-used timestamp
- revoked timestamp, when applicable
- provenance/source metadata

Provider credentials, access tokens, refresh tokens, private keys, and secrets MUST NOT be stored in the Principal or ordinary identity mapping payload.

## 10. Session boundary

Session state is distinct from conversation state.

```text
Authentication session
        ≠
Conversation workflow state
        ≠
Civic Case state
```

Session identifiers may be referenced by request context and audit records, but session secrets must remain within the secure authentication/session subsystem.

## 11. Privacy requirements

Identity data MUST follow Janavani's existing data-contract principles:

- data minimization
- purpose limitation
- explicit consent where required
- provenance for externally sourced identity facts
- retention controls
- access logging
- revocation handling
- legal deletion/anonymization where applicable
- separation of sensitive case content from general profile data

A channel adapter must not copy unnecessary profile information into every civic capability record.

## 12. PostgreSQL/RLS dependency

PostgreSQL RLS MUST NOT be implemented from channel identifiers or guessed ownership rules.

Before production RLS, the implementation must establish and verify:

1. canonical identity table/model
2. external identity mapping
3. authenticated session boundary
4. case ownership relationship
5. service-role versus user-role database access
6. row ownership predicates
7. privileged administrative access
8. sensitive-case isolation
9. audit requirements
10. migration, rollback, backup, and recovery behavior

Only after these are verified should SQL migrations and RLS policies be introduced.

## 13. Adapter requirements

Every interface adapter should eventually provide a normalized identity context without leaking provider-specific semantics into capabilities.

Example:

```text
Telegram Adapter
  Telegram user/chat identity
          ↓
  external identity mapping
          ↓
  Janavani Principal
```

The same capability must be callable through Web or Mobile without changing its domain ownership model.

## 14. Prohibited shortcuts

Do not:

- use Telegram `chat_id` as the canonical citizen ID
- use phone/email as the canonical primary identity
- authorize solely from an adapter-provided identifier
- equate authentication with consent
- equate authentication with case ownership without policy
- expose database credentials to AI agents
- allow AI to decide identity authorization
- implement RLS before identity ownership is verified
- persist access/refresh tokens in ordinary domain records

## 15. Implementation sequence

### Phase 1 — Contract

- identity persistence contract
- external identity mapping contract
- session boundary
- authentication assurance model
- authorization inputs

### Phase 2 — Provider adapter

Implement the first real authentication provider behind the contract. The provider must be replaceable without changing Civic Case or other capability contracts.

### Phase 3 — Durable identity storage

Implement PostgreSQL persistence only after the schema and access model are reviewed.

### Phase 4 — Authorization

Implement service-level authorization and verify its mapping to PostgreSQL roles/RLS.

### Phase 5 — Case integration

Bind `CivicCase.created_by` and case access to canonical Janavani identity rather than transport identifiers.

### Phase 6 — Security verification

Failure-test expired sessions, revoked identities, cross-user access, anonymous cases, privilege escalation, sensitive-case access, and provider-account unlinking.

## 16. Current repository status

The repository already contains a provider-neutral identity boundary under `src/identity`. The current verified implementation is a contract/context layer; a production authentication provider, durable identity repository, and PostgreSQL/RLS implementation are not established by this document.

This document is therefore an architectural contract, not a claim of production authentication readiness.
