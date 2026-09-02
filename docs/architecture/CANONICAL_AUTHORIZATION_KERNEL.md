# Canonical Authorization Kernel

**Status:** Implemented — provider-neutral foundation  
**Scope:** Shared Janavani authorization boundary

## Purpose

The authorization kernel separates authorization from identity, authentication,
consent, and capability execution. It provides one deterministic decision point
that can be consumed by Web, mobile, Telegram, WhatsApp, DApp, API, and future
adapters.

## Decision model

```text
Principal
  + Capability
  + Action
  + Resource
  + Context
  + Risk / approval requirement
        ↓
ALLOW / DENY / REQUIRE_APPROVAL
```

The implementation currently enforces capability possession and explicit risk/
approval gates. It does not implement database access, authentication, consent,
delegation, or RLS.

## Security boundary

The intended execution path is:

```text
Interface / Adapter
        ↓
Identity Context
        ↓
Authorization Kernel
        ↓
Consent / Purpose Gate
        ↓
Capability Service
        ↓
Repository
        ↓
PostgreSQL RLS
```

Authentication alone must not be treated as authorization. A resource identifier
also does not grant access by itself.

## Deliberate limitations

This first implementation is intentionally small. It does **not** yet claim to
solve:

- resource ownership or delegation;
- purpose-bound consent;
- service-identity policy;
- sensitive-case isolation;
- database RLS;
- audit persistence;
- policy configuration storage.

Those controls remain separate implementation gates and must be added without
moving authorization responsibility into transport adapters.

## Verification

The accompanying tests cover:

1. capability-based allow;
2. missing-capability denial;
3. anonymous denial for protected capability;
4. high-risk approval requirement;
5. explicit approval requirement;
6. denial taking precedence over an approval prompt when the capability is absent.

Before PostgreSQL RLS activation, this kernel must be extended or composed with
resource, delegation, consent, and service-identity policy and the negative-access
matrix in `CANONICAL_CASE_RLS_AUTHORIZATION_MATRIX.md` must pass.
