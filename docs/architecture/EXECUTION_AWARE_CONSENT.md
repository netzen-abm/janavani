# Execution-Aware Consent Enforcement

## Purpose

Consent must remain an independent permission control, while the canonical capability execution context establishes who is executing an operation. This boundary prevents a consent record for one identity from being reused by another execution context.

## Contract

```text
Authenticated Identity
        ↓
Capability Execution Context
        ↓
Consent Subject Binding
        ↓
Consent Requirement / Repository Check
        ↓
Capability
```

The enforcement helper performs two independent checks:

1. The execution identity must match the consent subject.
2. The consent requirement must be satisfied by the consent repository.

A mismatch or missing/invalid consent fails closed with `ConsentRequiredError`.

## Architecture rules

- Consent is not an authorization grant.
- Execution context is not a consent grant.
- Authorization remains the least-privilege capability authority.
- Consent remains the user-permission boundary where a capability requires it.
- A consent record cannot be replayed across execution identities.
- Provider and surface implementations do not become consent authorities.
- Existing consent semantics remain unchanged; this primitive binds them to execution identity.

## Scope boundary

This change establishes the shared execution-aware consent primitive and focused tests. It does not retrofit every existing capability or activate a production consent provider. Consequential capabilities can adopt it incrementally in bounded follow-up changes.
