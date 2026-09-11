# Janavani — Policy Composition Contract

**Status:** DESIGNED / INITIAL IMPLEMENTATION
**Date:** 12 September 2026

## Purpose

This contract defines how the canonical authorization kernel is composed with three independent policy controls:

1. explicit delegation;
2. purpose-bound consent;
3. service-identity policy.

The composition layer does not replace the canonical authorization kernel, identity/authentication, capability execution, repositories, or PostgreSQL RLS.

## Decision order

```text
Identity / Authentication
        ↓
Canonical Authorization Kernel
        ↓
Delegation Boundary (when acting for another principal)
        ↓
Purpose-Bound Consent (when the operation requires consent)
        ↓
Service-Identity Policy (for service credentials)
        ↓
Capability / Repository
        ↓
PostgreSQL RLS
```

A kernel `DENY` is terminal. Later gates cannot override it.

A kernel `REQUIRE_APPROVAL` remains `REQUIRE_APPROVAL` unless a later gate denies the request. Policy composition must never turn a denial into an approval or an approval requirement into an unconditional allow.

## Delegation

A delegation grant is explicit and bounded by:

- grantor principal;
- delegate principal;
- capability set;
- optional action set;
- optional resource set;
- expiry;
- revocation state.

An active delegation cannot escape its declared capability, action, or resource boundary.

A delegated operation must still pass the canonical authorization kernel. Delegation is an additional relationship constraint, not an authentication mechanism and not a substitute for capability authorization.

## Consent

Consent remains independent from authorization.

For ordinary execution, when a composed request declares a consent purpose/scope requirement, a granted consent must match the executing principal as subject, the exact purpose, and the exact requested scope.

For delegated execution, the consent subject may be the delegation grantor/resource owner. The request must identify that consent subject explicitly, and the subject must equal the validated delegation grantor. A delegate cannot select consent belonging to an unrelated principal.

Denied, revoked, expired, or otherwise non-granted consent cannot satisfy the gate.

A consent requirement with an incomplete purpose/scope is denied rather than interpreted permissively.

## Service identities

A principal authenticated with `SERVICE_CREDENTIAL` must have an explicit service policy.

The service policy is an allow-list of capability/action pairs. Service credentials therefore do not acquire general citizen authority merely because they are authenticated.

Database/RLS policy remains an independent enforcement layer.

## Failure rules

- missing or malformed delegation → `DENY`;
- revoked/expired delegation → `DENY`;
- delegation outside declared capability/action/resource → `DENY`;
- missing or mismatched required consent → `DENY`;
- delegated consent subject different from the validated grantor → `DENY`;
- service credential without explicit service policy → `DENY`;
- service action outside the allow-list → `DENY`;
- base authorization denial → terminal `DENY`;
- no gate may broaden authority implicitly.

## Deliberate non-goals

This initial implementation does not provide:

- persistent delegation storage;
- delegation lifecycle APIs;
- consent repository lookup;
- service-policy persistence;
- database RLS SQL;
- admin/operator bypass;
- multi-hop delegation;
- automatic consent inference;
- external provider-specific policy logic.

Those require separate contracts and verification before activation.

## Verification gate

Before PostgreSQL RLS activation, the implementation must add repository-backed policy tests proving that:

- revoked/inactive delegates cannot write;
- delegates cannot cross resource boundaries;
- consent cannot authorize a different purpose or scope;
- revoked/expired consent cannot authorize consequential action;
- delegated consent is attributable to the grantor/resource owner;
- service identities cannot perform unlisted actions;
- destination services cannot access unrelated cases;
- kernel denial remains terminal;
- authorization and RLS produce consistent decisions.
