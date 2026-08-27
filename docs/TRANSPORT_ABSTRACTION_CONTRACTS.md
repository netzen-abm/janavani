# JANAVANI — TRANSPORT ABSTRACTION CONTRACTS

**Status:** CANONICAL DESIGN CONTRACT — v1.0  
**Date:** 27 August 2026  
**Scope:** Shared transport boundary for Web, Telegram, Mini App, Android, iOS, DApp, SOS and future adapters.

## 1. Purpose

Define a provider-neutral transport contract so Janavani capabilities can use Internet, Telegram, mesh, local, satellite and optional decentralized transports without embedding transport-specific logic in domain capabilities.

This contract complements `docs/DATA_CONTRACTS.md`, `docs/CAPABILITY_REGISTRY.md` and `docs/PERMISSION_CONSENT_CONTRACTS.md`.

## 2. Architecture rule

```text
Capability
   ↓
TransportPolicy
   ↓
TransportRouter
   ↓
TransportAdapter
   ↓
Provider / device / network
```

Capabilities must not directly depend on a concrete Telegram, Redis, satellite, Reticulum, LoRa or other provider implementation.

## 3. Transport contract

```text
TransportAdapter
- adapter_id
- transport_type
- capabilities()
- health()
- estimate_cost()
- enqueue(message)
- transmit(message)
- query_delivery(delivery_id)
- cancel(delivery_id) where supported
```

Each adapter must return explicit state rather than inventing success.

## 4. Transport types

Canonical transport vocabulary:

```text
INTERNET
TELEGRAM
WHATSAPP
MESSENGER
RETICULUM
LORA
MESHTASTIC
BLUETOOTH
WIFI_DIRECT
SATELLITE
LOCAL
FREENET
OTHER
```

A channel and a transport are different concepts. Telegram is both a user-facing channel and, where appropriate, a messaging transport adapter; this distinction must remain explicit in contracts.

## 5. Adapter health

Every adapter exposes one of:

```text
AVAILABLE
DEGRADED
UNAVAILABLE
NOT_CONFIGURED
UNKNOWN
```

`AVAILABLE` means the adapter has sufficient evidence that it can currently attempt the requested operation. It does not mean delivery is guaranteed.

`NOT_CONFIGURED` means the provider integration has not been provisioned.

`UNKNOWN` must be used when the adapter cannot establish meaningful health state.

## 6. Message envelope

Transport-independent messages should use a stable envelope:

```text
TransportMessage
- message_id
- capability_id
- operation_id
- payload_ref
- payload_hash
- created_at
- expires_at (optional)
- priority
- sender_ref (optional)
- destination_ref
- consent_ref (optional)
- authorization_ref (optional)
- idempotency_key
- policy_version
```

The envelope references capability data rather than duplicating channel-specific business objects.

## 7. Delivery state machine

```text
CREATED
  ↓
QUEUED
  ↓
TRANSMITTING
  ↓
SENT
  ↓
RECEIVED
  ↓
ACKNOWLEDGED
```

Failure/terminal states:

```text
FAILED
EXPIRED
CANCELLED
UNKNOWN
```

State meanings:

- `CREATED`: message prepared locally.
- `QUEUED`: accepted by a local/outbound queue.
- `TRANSMITTING`: adapter is attempting transport.
- `SENT`: adapter/provider reports transmission accepted/sent according to its contract.
- `RECEIVED`: destination-side receipt is evidenced.
- `ACKNOWLEDGED`: destination/provider acknowledgement is evidenced.
- `FAILED`: transport attempt failed.
- `EXPIRED`: message validity window ended.
- `UNKNOWN`: state cannot currently be established.

A local queue is never proof of remote delivery.

## 8. Transport policy

A capability may declare a policy such as:

```text
TransportPolicy
- policy_id
- capability_id
- allowed_transports[]
- preferred_transports[]
- fallback_transports[]
- max_retries
- expiry_seconds
- allow_parallel_paths
- require_acknowledgement
- minimum_security_level
- data_classification
- policy_version
```

Emergency capabilities may use multiple paths when configured. Ordinary civic workflows should not automatically use emergency transports.

## 9. Routing rules

The router must consider:

1. capability policy;
2. user consent/permission;
3. data classification;
4. destination requirements;
5. adapter health;
6. expiry/priority;
7. cost constraints where configured;
8. retry limits;
9. acknowledgement requirements.

Routing must not silently downgrade a security/privacy requirement merely because a preferred transport is unavailable.

## 10. Internet / conventional API

The conventional network adapter is the default path for normal Web/API operations where configured.

Failure must surface as an unavailable/degraded workflow. It must not create synthetic local success.

## 11. Messaging channels

Telegram, WhatsApp and Messenger integrations must be channel adapters over the shared capability API.

They must not contain independent Case, Evidence, Authority or Document business logic.

A Telegram Bot and Telegram Mini App may share the same capability API while presenting different interaction surfaces.

## 12. Mesh

Mesh transport is an optional resilient transport family.

Supported adapter candidates:

- Reticulum/RNS;
- LoRa/RNode;
- Meshtastic;
- compatible local mesh adapters.

Each provider must be implemented as a real adapter before being reported as available. A scaffold/mock must report `NOT_CONFIGURED` or `UNAVAILABLE`.

Multi-hop and store-and-forward are required capabilities for the SOS mesh contract where supported.

## 13. Satellite

Satellite is an optional transport family. Provider/device integrations must be isolated behind adapters.

The platform must verify legal, regulatory, device and service availability for the deployment jurisdiction before representing a specific satellite service as supported.

Native device satellite and companion communicators are distinct adapters where required.

## 14. Local transport

Bluetooth, Wi-Fi Direct and local storage may support preparation, relay or store-and-forward capabilities.

Local persistence must never be represented as remote receipt.

## 15. Decentralized transport

Freenet, Nostr-related relay paths, blockchain anchoring and other decentralized infrastructure are optional adapters.

They must not become critical dependencies for ordinary civic workflows unless a capability contract explicitly requires them.

Unavailable decentralized infrastructure must leave unrelated capabilities functional.

## 16. Retry and idempotency

Adapters should support idempotent operation identifiers where the provider permits it.

Retries must:

- respect expiry;
- avoid uncontrolled duplicate submissions;
- preserve the original operation identity;
- record attempts;
- expose final/unknown state honestly.

For consequential government submissions, duplicate prevention is mandatory at the application workflow layer even if a provider lacks idempotency.

## 17. Security boundary

Transport adapters must not decide authorization.

The core/API must validate:

- identity/session where required;
- capability permission;
- consent;
- destination authorization;
- payload integrity;
- policy version.

The adapter receives only the data necessary to execute the already-authorized operation.

## 18. Privacy boundary

Transport selection must respect data classification.

For example:

```text
PUBLIC
INTERNAL
PERSONAL
SENSITIVE
HIGH_RISK
EMERGENCY
```

A transport that cannot satisfy the required privacy/security policy must be rejected even if it is otherwise available.

## 19. Observability

Every transport attempt should create an auditable delivery event containing:

- operation/message ID;
- adapter ID;
- transport type;
- attempt timestamp;
- resulting state;
- error code/reason where applicable;
- retry count;
- acknowledgement reference where applicable.

Avoid placing sensitive payload contents into ordinary logs.

## 20. Capability isolation

A provider outage must not cascade across unrelated capabilities.

Examples:

```text
Telegram unavailable
    → Web civic drafting remains available.

Redis unavailable
    → stateless public information paths may remain available if designed to do so.

Blockchain unavailable
    → evidence capture remains available without blockchain anchoring.

Mesh unavailable
    → ordinary Internet workflows remain available.

AI provider unavailable
    → non-AI document preparation remains available.
```

## 21. Minimum acceptance tests

- An unavailable adapter cannot report `SENT`.
- A local queue cannot produce `RECEIVED`.
- `RECEIVED` requires destination-side evidence.
- `ACKNOWLEDGED` requires an acknowledgement reference where the protocol supports one.
- Retry does not silently create a new business operation.
- A provider outage does not break unrelated capabilities.
- A Telegram adapter does not implement independent Case/Document business rules.
- A mock/scaffold adapter is never reported as available.
- Transport routing respects consent and permission contracts.
- Sensitive payloads are not emitted into ordinary logs.

## 22. Implementation status

This is a **canonical design contract**, not an implementation-complete claim. Each adapter must be mapped to repository code, tests, deployment configuration, security/privacy review and runtime evidence before it is marked complete in `docs/MASTER_TASK_CHECKLIST.md`.