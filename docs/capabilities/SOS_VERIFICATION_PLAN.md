# SOS Verification Plan

**Status:** Pre-implementation verification plan

## Gate 0 — Contract

The SOS capability contract must be reviewed before production implementation. See `docs/capabilities/SOS_CAPABILITY_CONTRACT.md`.

## Gate 1 — State machine

Verify that the implementation distinguishes:

- created;
- validated;
- transport selected;
- transmission attempted;
- accepted by transport;
- delivery confirmed;
- failed;
- timeout;
- unknown.

## Gate 2 — Location provenance

Verify that no default/fixed coordinate can be emitted as a real user location. Test permission denial, unavailable location, stale location and explicit user-provided location.

## Gate 3 — Transport isolation

Test Internet, Reticulum, Nym and future adapters independently. A failed adapter must return an explicit unavailable/failure state and must not fabricate an alternate success.

## Gate 4 — Delivery semantics

Create a controlled test backend that separately exposes acceptance and delivery-confirmation semantics. Prove that the client does not treat HTTP success as delivery confirmation unless the protocol contract explicitly establishes it.

## Gate 5 — Secret boundary

Verify that no backend credential is embedded in the distributed WebAssembly/client artifact. Secret-bearing operations must use an appropriate secure boundary.

## Gate 6 — Privacy/wipe semantics

Verify exactly which local data is removed by a wipe operation. Test that the UI never calls local deletion a global/remote wipe.

## Gate 7 — Failure isolation

Simulate failure of every transport and access surface. Core civic workflows must remain independent. SOS degradation must be explicit and must not corrupt unrelated capabilities.

## Gate 8 — End-to-end evidence

Run a controlled end-to-end emergency test with a non-production endpoint. Record request identifier, transport acknowledgement, delivery acknowledgement and failure/recovery behavior without recording unnecessary personal data.

## Gate 9 — Production gate

Production status requires all gates to pass, documentation to be updated in the same change set, and the capability truth inventory to change from `UNVERIFIED` only when executable evidence supports the new status.
