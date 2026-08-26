# Decentralized Transport Architecture

**Status:** Architecture authority / implementation planning
**Date:** 2026-08-26

## Purpose

Define how Janavani can add Nostr, Freenet, Nym, Reticulum, blockchain/ZKP and future Web3/Web4/Web5 transports without coupling user-facing applications to one another or requiring a rebuild of the ecosystem.

## Core rule

A transport is a shared capability, not an access surface.

Android, iOS, Web, DApp, Telegram, Telegram Mini App, WhatsApp, Messenger, CLI and future surfaces may consume the same capability contract through independent adapters. No access surface may depend on another access surface at runtime.

## Reference model

```text
                    JANAVANI CAPABILITY CONTRACTS
                              |
                    capability / policy layer
                              |
       +----------------------+----------------------+
       |                      |                      |
     Nostr                 Freenet             Privacy Mesh
       |                      |                /           \
   relay adapter       contract/delegate     Nym        Reticulum
       |                      |                |             |
       +----------------------+----------------+-------------+
                              |
                    transport-neutral result
                              |
              +---------------+---------------+
              |                               |
        Web / Android / iOS / DApp      Telegram / WhatsApp /
              |                         Messenger / future
              +-------------------------------+
```

## Capability boundaries

### Nostr

Role: decentralized event/relay transport and, where deliberately implemented, decentralized web publishing.

Required boundary:

- key loading and validation;
- relay configuration;
- event signing;
- publish/read/subscribe semantics;
- acknowledgement state;
- timeout/retry policy;
- privacy-safe logging.

`NOSTR_PRIVATE_KEY_HEX` is runtime secret configuration only. A configured secret is not proof of a working Nostr integration.

### Freenet

Role: decentralized contract/state execution and storage surface.

Treat Contract, Delegate, and UI as separate responsibilities. Do not treat Freenet as a generic replacement for the canonical API. Contract identity/build reproducibility must be tracked explicitly before production deployment.

### Nym

Role: privacy-preserving network transport. It is not the civic domain authority and is not required for unrelated capabilities.

### Reticulum

Role: resilient peer-to-peer/mesh transport. Internet, tunnel, and physical radio interfaces are transport implementations, not application business logic.

### Blockchain / ZKP

Role: verifiable integrity, proof, anchoring, or other explicitly defined cryptographic capabilities. String-shape validation is never proof verification.

## User optionality

Optional means **user choice**. The ecosystem retains the capability regardless of whether an individual user enables it or whether a particular access surface exposes it.

Example:

`User chooses Nostr = no` does not mean `Janavani lacks Nostr capability`.

## Independence and failure isolation

Expected isolation:

- Nostr failure must not prevent core civic workflows.
- Freenet failure must not prevent Web/Android/iOS operation.
- Nym failure must not prevent normal Internet transport.
- Reticulum failure must not prevent other transports.
- AI/provider failure must not prevent non-AI civic/document workflows.
- Telegram failure must not prevent WhatsApp, Messenger, Web, Android, iOS or DApp operation.

## Evidence states

Each transport must be classified as `VERIFIED`, `PARTIALLY VERIFIED`, `CONFIGURED`, `UNVERIFIED`, `FAILED`, or `BLOCKED`.

A mock adapter may verify a contract boundary only. A provider diagnostic may verify provider reachability only. Neither is production end-to-end evidence.

## Implementation sequence

1. Define capability contract.
2. Define security/privacy boundary.
3. Implement provider/transport-neutral adapter interface.
4. Implement deterministic unit tests.
5. Implement controlled integration tests.
6. Implement negative/failure-isolation tests.
7. Verify real transport behavior.
8. Document evidence and operational requirements.
9. Only then consider production deployment.

## Prohibited patterns

- hard-coded protocol identities;
- synthetic success responses;
- client-specific protocol implementations duplicated across surfaces;
- secrets in source or test fixtures;
- claiming deployment from configuration alone;
- disabling failed verification to obtain green CI;
- introducing a second runtime authority for a transport.

## Future extensibility

New transports should implement the existing capability boundary rather than modify every client. This permits future Web3/Web4/Web5 or other protocols to be added as plug-in capability adapters while preserving independent operation of existing surfaces.
