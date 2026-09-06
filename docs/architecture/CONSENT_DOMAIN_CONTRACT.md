# Janavani — Canonical Consent Domain Contract

**Status:** CANONICAL DESIGN CONTRACT — controlled implementation
**Scope:** Consent as an independent reusable domain capability

## 1. Purpose

Consent is an explicit, purpose-bound and scope-bound domain object. A
consent reference inside `CivicCase` is not itself consent and cannot supply
missing purpose, scope, grant or provenance semantics.

The capability is independent of Web, Telegram, mobile, DApp, database and
provider implementations.

## 2. Canonical object

```text
Consent
  consent_id: string
  subject_id: string
  purpose: string
  scope: string[]
  grant_type: EXPLICIT | REQUIRED_BY_DESTINATION | NOT_REQUIRED
  status: GRANTED | DENIED | REVOKED | EXPIRED
  created_at: datetime
  expires_at: datetime|null
  revoked_at: datetime|null
  proof_ref: string|null
```

These fields are already defined by the canonical data contract. The
implementation must not invent additional semantics during persistence.

## 3. Invariants

- `consent_id` is stable and identifies one consent record.
- `subject_id` identifies the entity whose consent is represented.
- `purpose` must be explicit and non-empty.
- Required consent must have an explicit scope.
- Revoked consent must carry a revocation timestamp.
- Only `GRANTED` consent is currently authorization-positive.
- Authorization requires both matching purpose and requested scope.
- Expired and revoked consent are not authorization-positive.
- A case reference does not bypass expiry or revocation checks.
- Authentication or channel access does not imply consent.

## 4. Repository boundary

```text
Surface / application use case
            |
            v
     ConsentRepository
            |
            v
     Durable provider
```

The repository persists complete `Consent` objects. It must not manufacture
purpose, scope, grant type, status, timestamps or proof references.

Repeated persistence of the same identifier is idempotent only when the
complete object is equivalent. Conflicting reuse of an identifier is rejected.

## 5. Case relationship

`CivicCase.consent_refs` remains a relationship/reference projection. It does
not replace the independent consent record.

Before durable consent persistence is activated, callers must possess a
canonical `Consent` object. No compatibility bridge may synthesize one from
a string such as `telegram:<case>:submission`.

## 6. Cross-channel rule

Consent semantics are channel-neutral. A Web, Telegram, mobile or future
surface may present or collect consent differently, but all surfaces must
produce the same canonical domain meaning.

## 7. Security boundary

Consent authorization must be evaluated at the time an optional use occurs.
Historical consent references alone are insufficient because consent may be
expired or revoked.

## 8. Non-goals

This contract does not yet define:

- legal text or jurisdiction-specific wording;
- UI presentation or button labels;
- identity verification policy;
- database migration or RLS policy;
- submission transport authorization;
- automatic consent renewal;
- retention or deletion rules beyond the existing privacy contracts.

Those concerns remain separate contracts and production gates.
