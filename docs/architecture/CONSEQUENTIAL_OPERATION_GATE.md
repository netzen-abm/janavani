# Consequential Operation Gate

## Purpose

The Consequential Operation Gate is the shared, provider-neutral control-plane boundary for operations that can mutate Janavani state or cause an external side effect.

It composes independent controls; it does not replace them.

```text
Authenticated Identity
        ↓
Authorization / Policy Decision
        ↓
Consent (when required)
        ↓
Explicit User Approval (when required)
        ↓
Capability Execution Context
        ↓
Capability / Side Effect
```

## Non-negotiable rules

1. Authorization remains the authority for capability-level least privilege.
2. Execution context is consistency and traceability context, not an authorization grant.
3. Consent is an independent user-permission control and is fail-closed.
4. Explicit approval is distinct from both authorization and consent.
5. A denied authorization cannot be overridden by consent or approval.
6. A missing required consent cannot be overridden by authorization or approval.
7. An operation requiring approval cannot execute without explicit approval.
8. External side effects must retain the execution envelope's idempotency requirement.
9. The gate is independent of Web, Telegram, mobile, AI, storage providers, and delivery providers.
10. AI or agentic output cannot make a consequential operation authoritative by itself.

## Decision model

The gate returns one deterministic outcome:

- `ALLOW` — all required controls permit execution.
- `DENY` — authorization or execution-context consistency rejects the operation.
- `CONSENT_REQUIRED` — required consent is missing or unavailable.
- `REQUIRE_APPROVAL` — the operation is authorized but explicit user approval is still required.

Authorization denial has precedence over downstream controls. Consent is evaluated before an approval-required result so the caller can discover every mandatory control boundary without treating approval as a substitute for consent.

## Scope boundary

This primitive does not execute capabilities, persist policy decisions, introduce a provider, or retrofit every existing capability. It establishes the common decision boundary first. Existing capability implementations remain responsible for their own domain invariants until they are migrated in bounded follow-up changes.
