# Archived fake decentralized driver

**Original path:** `src/web_dioxus/src/decentralized_drivers.rs`
**Archived:** 2026-08-26

## Reason

The implementation returned hard-coded Nostr keys, hard-coded Nym/Reticulum success responses, and performed only superficial blockchain input validation. It therefore did not constitute a real implementation of those capabilities and could falsely report success.

The original source is preserved in Git history and this archive records why it must not be treated as production capability evidence.

## Required replacement

Use explicit capability contracts and adapters. Until a real protocol implementation is wired and verified, return a truthful unsupported/unavailable result rather than synthetic success.

**No-fake-green rule:** mocks may test an adapter boundary, but hard-coded fake success must never be presented as a functioning protocol implementation.
