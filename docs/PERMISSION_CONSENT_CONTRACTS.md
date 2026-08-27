# JANAVANI — PERMISSION & CONSENT CONTRACTS

**Status:** CANONICAL DESIGN CONTRACT — v1.0  
**Date:** 27 August 2026  
**Scope:** Shared across Web, Telegram, Mini App, Android, iOS, DApp and future channels.

## 1. Purpose

Define the permission and consent boundary used by Janavani capabilities. A channel may present a consent UI, but it must not invent capability-specific permission rules or silently broaden consent.

This contract complements `docs/DATA_CONTRACTS.md` and `docs/CAPABILITY_REGISTRY.md`.

## 2. Core principles

1. Consent is purpose-bound.
2. Consent is explicit unless a documented product/legal rule says it is not required.
3. One capability's consent must not silently authorize another capability.
4. Optional data use is opt-in.
5. Consent can be denied, revoked or expired.
6. Revocation applies to future processing unless a retention/legal requirement requires preservation.
7. A channel may authenticate a user without automatically linking identities across channels.
8. Emergency behavior must remain truthful about what was authorized, attempted and delivered.
9. The platform must collect the minimum data needed for the declared capability.
10. Consequential external actions require an explicit user approval gate where applicable.
11. Consent records are auditable and versioned.
12. Provider failure must not be represented as user consent or successful execution.

## 3. Permission model

A permission answers: **may this actor perform this operation?**

```text
Permission
- permission_id
- subject_id
- capability_id
- action
- resource_type
- resource_id (optional)
- decision: ALLOW | DENY
- scope
- issued_at
- expires_at (optional)
- revoked_at (optional)
- policy_version
- source_channel
```

Permissions must be evaluated server-side for consequential operations. Client-side checks are UX aids, not security boundaries.

## 4. Consent model

A consent answers: **has the subject knowingly authorised this declared purpose?**

```text
Consent
- consent_id
- subject_id
- capability_id
- purpose
- scope[]
- data_categories[]
- grant_type: EXPLICIT | REQUIRED_BY_DESTINATION | NOT_REQUIRED
- status: GRANTED | DENIED | REVOKED | EXPIRED
- policy_version
- granted_at
- expires_at (optional)
- revoked_at (optional)
- proof_ref (optional)
- source_channel
```

This is aligned with the canonical `Consent` data object in `docs/DATA_CONTRACTS.md`.

## 5. Capability consent scopes

### 5.1 Civic drafting

May permit:

- processing the supplied narrative;
- creating a draft Case;
- generating a draft Document;
- retaining the draft according to the declared retention policy.

Does **not** automatically permit submission to a government authority.

### 5.2 Evidence capture

Must separately identify:

- evidence category;
- storage purpose;
- retention period/policy;
- optional location metadata;
- optional AI/OCR processing.

Location must not be collected merely because the device can provide it.

### 5.3 External submission

Requires an explicit approval boundary before transmission unless the destination protocol or documented safety rule provides otherwise.

The approval must identify, where practical:

- destination;
- document/package version;
- attachments;
- identity/contact information being transmitted;
- transport/channel;
- applicable consent/policy version.

### 5.4 Cross-channel linking

Web, Telegram, Mini App, Android, iOS and DApp identities remain separate by default.

Linking requires explicit consent and must create an auditable relationship. Authentication alone is insufficient.

### 5.5 Public attribution

Public display of contributor identity, photo, amount or similar information requires a separate preference/consent decision. Private contribution does not imply public attribution.

### 5.6 Analytics

Analytics consent must remain separate from civic-service consent unless a documented required-by-destination rule applies. Analytics must follow data minimisation and the canonical privacy-preserving analytics boundary.

### 5.7 Emergency/SOS

SOS preferences must identify authorised recipients and escalation policy. Location sharing must follow the user's configured SOS preference and applicable emergency requirements.

An SOS client must never claim that an authority/contact was notified merely because an SOS packet was locally created or queued.

## 6. Human approval gates

The following actions require explicit confirmation before execution unless an approved safety policy says otherwise:

- external government submission;
- publication of a citizen review;
- public attribution of a contribution;
- cross-channel identity linking;
- high-risk whistleblower routing;
- consequential AI-agent action;
- irreversible or materially privacy-impacting operation.

The approval should bind to the specific operation/version rather than being an indefinite blanket approval.

## 7. Revocation

When consent is revoked:

1. stop future optional processing;
2. stop future optional sharing;
3. invalidate dependent future actions where feasible;
4. preserve only information required by retention, legal, security or audit obligations;
5. record the revocation event.

Revocation must not be represented as retroactive deletion where preservation is legally required.

## 8. Failure semantics

```text
NOT_REQUESTED
     ↓
REQUESTED
     ↓
GRANTED / DENIED
     ↓
AUTHORIZED_OPERATION
     ↓
ATTEMPTED
     ↓
CONFIRMED / FAILED / UNKNOWN
```

`GRANTED` means consent/permission exists. It does **not** mean the operation succeeded.

`ATTEMPTED` does **not** mean delivered.

Only an appropriate provider acknowledgement may establish confirmed external delivery.

## 9. Channel responsibilities

### Client/channel

- explain purpose and scope;
- obtain user decisions;
- show current status;
- avoid collecting unnecessary data;
- never treat client checks as authorization enforcement.

### Core/API

- validate permission and consent;
- enforce policy;
- bind approval to the intended operation;
- create audit events;
- prevent cross-capability consent leakage.

### Provider adapter

- execute only authorized operations;
- return truthful transport/provider state;
- never convert local persistence into delivery confirmation.

## 10. Audit requirements

Permission and consent events should produce an `AuditEvent` containing, where applicable:

- actor/subject;
- capability;
- action;
- object;
- timestamp;
- source channel;
- policy/contract version;
- result;
- reason for denial/failure.

Sensitive values must not be copied into ordinary audit metadata unnecessarily.

## 11. Minimum acceptance tests

- A denied consent prevents optional processing.
- Revoked consent prevents future optional sharing.
- Civic drafting consent cannot authorize external submission.
- Analytics consent cannot authorize evidence access.
- Cross-channel linking requires an explicit linking decision.
- Client-side permission state cannot bypass server authorization.
- A queued SOS cannot be displayed as delivered.
- An attempted government submission cannot be displayed as acknowledged without acknowledgement evidence.
- Consent records preserve policy version and source channel.

## 12. Implementation status

This document is a **design contract**. It does not claim that every permission/consent workflow is implemented.

Implementation completion requires repository code, tests, security/privacy review where applicable, runtime verification and evidence in the master checklist.