# Civic Case Contract Conformance Gate — Initial Implementation

**Status:** VERIFYING  
**Scope:** Python ↔ Rust canonical Civic Case vocabulary and serialization

This gate is intentionally narrow. It does not change domain semantics. It makes the already-existing parity requirement executable.

## Required parity

The Python and Rust kernels must expose identical serialized values for:

- `CaseType`
- `CaseStatus`
- `CaseEventType`

The canonical source values are the serialized contract values, not language-specific enum identifiers.

## Current evidence

The inspected Python and Rust implementations currently expose matching `CaseType`, `CaseStatus`, and `CaseEventType` values, including `citizen_verified` and `citizen_reopened`.

Existing Rust serialization tests and Python contract tests provide partial evidence. A machine-readable parity fixture should become the durable cross-language gate.

## Deliberate non-goals

This gate does not yet assert:

- complete transition implementation parity;
- provider behavior parity;
- authorization parity;
- persistence transaction parity;
- cross-surface runtime parity.

Those require separate tests because serialization equality alone cannot prove behavioral equivalence.

## Next gate

After this vocabulary/serialization gate, add behavioral parity fixtures for lifecycle transitions and submission/acknowledgement semantics.