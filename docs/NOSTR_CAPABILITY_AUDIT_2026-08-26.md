# Nostr Capability Audit — 2026-08-26

## Executive conclusion

**Nostr is not currently production-verified in the canonical Janavani architecture.**

The repository contains a real-looking legacy Python publishing helper, but it lives under `archive/services_legacy/nostr_client.py`. It reads `NOSTR_PRIVATE_KEY_HEX`, constructs signed events, and publishes them through configured relays when its dependencies and credentials are present. That is useful implementation evidence, but its archived location means it is not the canonical runtime path.

The current Dioxus decentralized driver is not valid Nostr implementation evidence. It previously returned hard-coded synthetic `npub`/`nsec` values. That implementation has been archived as fake capability evidence and must not be used as proof of Nostr functionality.

The older Rust `janavani_v2/src/protocols/nostr.rs` is also not production evidence: it returns another hard-coded keypair and formats a string rather than publishing an actual Nostr event.

## Evidence classification

| Layer | Evidence | Status |
|---|---|---|
| Secret configuration | `NOSTR_PRIVATE_KEY_HEX` documented/configured as runtime secret name | CONFIGURED only |
| Legacy Python publisher | Uses `python-nostr`, signs events, opens relays and publishes | LEGACY IMPLEMENTATION; integration not currently verified |
| Dioxus decentralized driver | Hard-coded identity/synthetic success behavior | INVALID / ARCHIVED |
| `janavani_v2` Rust driver | Hard-coded identity and string formatting only | LEGACY / UNVERIFIED |
| Canonical capability adapter | No verified canonical Nostr adapter established by this audit | UNVERIFIED |
| Real relay publish | No current canonical end-to-end evidence recorded | UNVERIFIED |
| Key lifecycle/security | Secret name standardized, but runtime ownership/rotation path needs explicit verification | PARTIALLY VERIFIED |

## Secret boundary

Canonical environment variable name:

`NOSTR_PRIVATE_KEY_HEX`

The private key must remain outside source control and must never appear in logs, client bundles, test fixtures, documents, capability responses, telemetry, or AI prompts.

The secret being configured does not itself prove that Nostr works.

## Required canonical implementation

Create a shared Nostr capability contract and provider-neutral adapter boundary. The adapter should own:

- key loading and validation;
- public-key derivation;
- relay configuration;
- event construction/signing;
- publish acknowledgement semantics;
- read/subscribe semantics where required;
- relay failure handling;
- timeout/retry policy;
- privacy and logging controls;
- explicit delivery/acknowledgement state.

User-facing clients must consume this capability independently. They must not each implement Nostr protocol logic.

## Verification required before production status

1. Unit tests for event/key contract behavior without exposing secret material.
2. Integration test against a controlled/test relay or deterministic local relay fixture.
3. Explicit negative tests for missing/invalid key, unavailable relay, timeout and partial relay success.
4. End-to-end publish verification proving an event accepted by the relay and returning the expected event identifier.
5. Security review of private-key lifecycle and memory/log handling.
6. Documentation update with the actual adapter location and evidence level.
7. Failure-isolation verification showing that Nostr failure does not prevent core civic, document, storage or other client capabilities from operating.

## No-fake-green rule

Do not restore the hard-coded Dioxus/Rust behavior merely to make a UI or CI test pass. If the real adapter is not yet implemented, the capability must remain explicitly `UNVERIFIED` or `UNAVAILABLE`.

## Related architecture

The ecosystem capability matrix identifies Nostr as a user-selectable capability requiring an independent adapter. The matrix is a scope register and explicitly does not claim that every row is already implemented.
