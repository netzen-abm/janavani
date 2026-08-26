# Archived SOS fake-dispatch record

**Original path:** `src/services/emergency_sos.py`
**Archived:** 2026-08-26

## Reason

The prior SOS service constructed a dictionary that looked like a Nostr Kind-4 event and returned `nostr_distress_signal_dispatched: true`, but it did not sign or publish anything to a Nostr relay. It also returned a synthetic event identifier as a fingerprint. This was not protocol evidence.

The service additionally described Redis deletion as a complete data wipe and logged success-like language. Those claims exceeded the evidence available from the operations performed.

## Replacement direction

Retain only locally verifiable cleanup/revocation operations in the SOS service. Nostr dispatch must be a separate real transport adapter behind the SOS capability contract and may report acceptance/delivery only according to explicit protocol evidence.

**Archive-first rule:** the historical source remains recoverable in Git history. No production capability should be inferred from this archived implementation.
