# Decentralized Capability Verification Plan

**Status:** Planning / evidence gate
**Date:** 2026-08-26

## Objective

Verify decentralized capabilities independently and truthfully before production deployment. This document does not claim that any listed capability is currently production-ready.

## Workstream order

### D0 — Repository and security baseline

- remove/archival-review synthetic protocol implementations;
- standardize secret names;
- verify no private keys are committed or logged;
- classify current implementations as canonical, legacy, experimental, or invalid;
- keep known failures visible.

### D1 — Nostr

- establish shared Nostr capability contract;
- implement key/relay adapter without client coupling;
- test key validation without exposing secrets;
- controlled relay integration test;
- publish acknowledgement test;
- timeout, unavailable relay, partial relay success and invalid-key tests;
- verify failure isolation;
- only then consider deployment/web-hosting automation.

Current status: **UNVERIFIED**.

### D2 — Freenet

- verify current Freenet toolchain/version;
- create minimal Contract/Delegate/UI laboratory;
- reproduce contract build deterministically;
- verify local node operation;
- test contract state flow;
- test delegate/private-state boundary;
- record build metadata and Contract ID;
- controlled network deployment;
- failure and recovery testing;
- only then evaluate Janavani production deployment.

Current status: **UNVERIFIED / RESEARCH**.

### D3 — Nym

- verify actual client/daemon version;
- define transport adapter;
- local connectivity test;
- real request/response integration test;
- daemon unavailable/timeout tests;
- privacy/logging review;
- verify fallback to another transport.

Current status: **UNVERIFIED**.

### D4 — Reticulum

- verify Reticulum version and supported interfaces;
- software-only two-node test first;
- encrypted application message test;
- failure/reconnect test;
- Internet/tunnel interface test;
- only after software transport is stable, test RNode/LoRa hardware;
- document region-specific radio configuration separately from application code.

Current status: **UNVERIFIED**.

### D5 — Blockchain / ZKP

- define exactly what is being proven;
- select canonical cryptographic/proof library;
- implement real verification adapter;
- positive and negative proof tests;
- reject malformed/invalid proofs;
- do not treat hashes, prefixes, or string shape as proof verification;
- verify chain/provider failure isolation.

Current status: **UNVERIFIED**.

## Production gate

A decentralized capability cannot be marked production-ready until all applicable gates pass:

1. contract exists;
2. implementation is real rather than synthetic;
3. deterministic tests pass;
4. real integration evidence exists;
5. negative/failure-mode tests pass;
6. secret/privacy boundary is reviewed;
7. failure isolation is demonstrated;
8. documentation matches the implementation;
9. deployment/recovery procedure is reproducible;
10. CI records the evidence without suppressing failures.

## Deployment rule

Do not deploy Janavani production state to a decentralized network merely because the code compiles or credentials exist. Deployment follows verification, not the reverse.
