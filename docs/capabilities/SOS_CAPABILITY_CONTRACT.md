# Janavani SOS Capability Contract

**Status:** Contract / safety review baseline  
**Evidence level:** UNVERIFIED  
**Date:** 2026-08-26

## Purpose

Define the safety-critical contract for emergency distress handling before a real transport implementation is restored.

This document does not claim that SOS delivery is currently operational.

## Safety principles

1. Privacy and safety are by design and by default.
2. No fabricated location, identity, delivery state, transport state, or acknowledgement.
3. A user-facing success message must correspond to the strongest evidence actually available.
4. Failure of one transport must not silently imply success through another.
5. Local data deletion is distinct from remote deletion and must never be described as global deletion.
6. User optionality means the user chooses whether to use the capability; the ecosystem retains the capability.
7. Safety-critical behavior must not depend on another access surface remaining online.

## Lifecycle

```text
CREATED
  |
  v
VALIDATED
  |
  v
TRANSPORT_SELECTED
  |
  v
TRANSMISSION_ATTEMPTED
  |
  +----> FAILED
  |
  v
ACCEPTED_BY_TRANSPORT
  |
  +----> TIMEOUT / UNKNOWN
  |
  v
DELIVERY_CONFIRMED
```

The implementation may add states, but must not collapse `ACCEPTED_BY_TRANSPORT` into `DELIVERY_CONFIRMED` without evidence.

## Evidence semantics

### CREATED
The client has created a local emergency request.

### VALIDATED
Required fields and local safety constraints passed validation. Location must be supplied by a trusted source or explicitly marked unavailable; the system must never substitute a fixed or guessed location.

### TRANSPORT_SELECTED
A configured transport adapter has been selected according to policy. Selection is not evidence of availability.

### TRANSMISSION_ATTEMPTED
A transport operation was actually invoked.

### ACCEPTED_BY_TRANSPORT
The transport/backend has explicitly acknowledged receipt/acceptance according to its protocol. This is not proof that an emergency recipient received or acted on the alert.

### DELIVERY_CONFIRMED
A separate, protocol-specific acknowledgement proves delivery to the intended emergency endpoint. HTTP `2xx` alone is not sufficient unless the backend contract explicitly defines and proves delivery semantics.

### UNKNOWN
The system cannot determine whether delivery occurred. The UI must say so rather than report success.

## Required transport abstraction

```text
SOS capability contract
        |
        +-- Internet adapter
        +-- Reticulum adapter
        +-- Nym adapter (when appropriate)
        +-- Future emergency transport
```

Each adapter must expose explicit result semantics and must not own the SOS domain lifecycle.

## Failure isolation

- Reticulum unavailable -> online/other verified transport may still be considered according to policy.
- Internet unavailable -> Reticulum or another verified transport may be considered.
- Nym unavailable -> unrelated transports remain independent.
- Backend unavailable -> local emergency state must not be reported as delivered.
- AI unavailable -> SOS must remain usable without AI unless a clearly optional AI-assisted feature is being used.
- Any client surface failure -> other independently operating surfaces must remain unaffected.

## Privacy boundary

The client must not embed reusable backend credentials in distributed WebAssembly/client code. Secret-bearing operations belong behind an appropriate server-side or dedicated secure capability boundary.

The local wipe operation, if offered, must state exactly what it clears. Browser local-storage deletion does not erase server state, remote caches, backups, logs, recipient devices, or other copies.

## Location boundary

Location provenance must be explicit. Possible states include:

- `VERIFIED_DEVICE_LOCATION`
- `USER_PROVIDED_LOCATION`
- `LOCATION_UNAVAILABLE`
- `LOCATION_STALE`
- `LOCATION_PERMISSION_DENIED`

No implementation may silently convert unavailable location into a fixed coordinate.

## User messaging requirements

Avoid:

- "Emergency delivered" without delivery evidence.
- "Cache wiped globally" after local storage deletion.
- "Reticulum active" when the adapter is unavailable.
- "Location" when the value was fabricated or is merely a stale/default value.

Prefer precise messages such as:

- "Emergency request created locally."
- "Transport accepted the request; delivery is not confirmed."
- "Emergency transport unavailable."
- "Delivery status unknown."

## Verification gates

Before production status:

1. Unit-test lifecycle/state transitions.
2. Test missing and invalid location handling.
3. Test each transport's unavailable/timeout/failure path.
4. Test backend acceptance separately from delivery confirmation.
5. Test that client secrets are absent from the built client artifact.
6. Test local wipe semantics and document its exact scope.
7. Run controlled end-to-end delivery tests against a test endpoint.
8. Verify independence when each transport and each client surface is unavailable.
9. Record evidence and update `docs/CAPABILITY_TRUTH_INVENTORY.md`.
10. Update `docs/KNOWN_FAILURES.md` when a gate fails; never weaken the gate to obtain green CI.

## Current implementation status

The current Web/Dioxus SOS implementation is **UNVERIFIED**. Reticulum is not a verified adapter, and the backend delivery contract is not established. Production deployment must remain blocked until the verification gates above are satisfied.
