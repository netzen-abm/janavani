# Archived canonical protocol implementation record

**Original path:** `src/lib.rs`
**Archived:** 2026-08-26

## Reason for archival

The prior canonical Rust library exposed Nostr, Nym, Reticulum, ZKP, blockchain and Freenet functions that returned success without performing the corresponding protocol operations. The ZKP implementation explicitly returned a dummy proof byte array; other implementations printed success-like messages and returned `Ok(())` without transport, signing, verification, anchoring, or decentralized state synchronization.

This is confirmed fake capability behavior and must not be treated as protocol implementation or production verification evidence.

## Replacement

The active implementation will retain feature isolation and capability boundaries but return a truthful `CapabilityUnavailable` result until each real adapter is implemented and verified.

**Rule:** do not restore synthetic success merely to satisfy feature-activation tests or CI.
