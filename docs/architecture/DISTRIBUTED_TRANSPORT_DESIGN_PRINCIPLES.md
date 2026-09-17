# Janavani Distributed Transport Design Principles

**Status:** Research-derived architectural guidance  
**Source inspiration:** Reticulum / LXMF / Nomad Network materials reviewed 2026-09-17  
**Important:** These principles are adopted as Janavani design guidance, not as a commitment to the Reticulum protocol or its implementation.

## 1. Cost is multidimensional

Treat transmission cost as more than network bandwidth. A payload may consume:

- bytes and airtime;
- battery/energy;
- radio or device processing;
- storage capacity at intermediate nodes;
- retry opportunities;
- user attention and latency budget.

The transport layer should therefore expose enough metadata for a policy or routing layer to select an appropriate representation and delivery strategy.

## 2. Minimum sufficient representation

Every capability should distinguish semantic intent from transport representation.

The canonical capability should produce a compact, provider-neutral message model. A transport adapter may encode it differently for Internet, mesh, radio, delayed synchronization, or other media.

Do not force a large JSON/domain object onto constrained transports when a smaller representation preserves the same meaning.

## 3. Context-before-payload

Prefer references to already-known context over repeated metadata where the receiving side can safely resolve that context.

Examples include:

- opaque case/reference identifiers instead of repeated profile fields;
- destination references instead of repeated recipient metadata;
- evidence references instead of embedding raw evidence in control messages;
- schema/version identifiers instead of repeating descriptive field names.

This optimization must never remove information required for authorization, provenance, integrity, or safe interpretation.

## 4. Asynchronous-first transport

Janavani capabilities must not assume that an external destination is continuously reachable.

Transport contracts should support:

`CREATE → QUEUE → FORWARD → ACCEPT → DELIVER → ACKNOWLEDGE`

with truthful intermediate and terminal states. Store-and-forward is a first-class mode for suitable capabilities, not merely an exceptional fallback.

## 5. Offline capability

A surface or node should be able to preserve an intent locally when appropriate and communicate it later without pretending it was already delivered.

The local record must preserve enough provenance and idempotency information to prevent accidental duplicate actions when connectivity returns.

## 6. Identity independent of location

Where the transport supports portable cryptographic identities, keep identity separate from network location. A person/device should be able to change interface or connectivity without forcing application-level identity changes.

Janavani should not make network location part of the semantic identity of a citizen or capability.

This does not require Janavani to adopt Reticulum identity semantics wholesale.

## 7. Hostile-medium assumption

Transport adapters should assume the medium and intermediate infrastructure may be unavailable, observable, compromised, delayed, duplicated, or reordered.

Confidentiality, integrity, replay resistance, authentication, and provenance must therefore be explicit protocol concerns rather than assumptions based solely on a trusted network path.

## 8. Capability messages should be intentionally small

Introduce transport-level message classes rather than sending arbitrary application payloads everywhere:

- `CONTROL` — small state/intent transitions;
- `REFERENCE` — identifiers referring to previously registered data;
- `EVIDENCE_DESCRIPTOR` — hashes, provenance, size/class, and retrieval instructions where appropriate;
- `CONTENT` — actual payload data when necessary;
- `ACK` — delivery/receipt/processing acknowledgement;
- `ERROR` — bounded machine-readable failure information.

A small control message should not automatically pull or transmit the referenced content.

## 9. Priority and urgency must be semantic

Do not equate emergency with "send everything immediately".

An emergency message may need:

1. immediate tiny control signal;
2. minimal essential context;
3. queued evidence references;
4. larger evidence payloads only when transport capacity and policy permit.

This supports graceful degradation and reduces the chance that a large attachment prevents the critical signal from getting through.

## 10. Delivery truth

Transport success must be represented with a typed state machine, not a generic boolean such as `sent=true`.

At minimum distinguish:

`LOCAL_ONLY`, `QUEUED`, `TRANSMITTING`, `ACCEPTED`, `DELIVERED`, `ACKNOWLEDGED`, `FAILED`, `UNKNOWN`.

Different transports may legitimately terminate at different states.

## 11. Retry and idempotency

Retries are expected in intermittent networks. Every consequential external operation must therefore have an idempotency key and operation identifier.

A transport adapter may retry delivery, but it must not silently repeat a consequential operation merely because a prior outcome is unknown.

Unknown outcome should trigger reconciliation, not blind duplication.

## 12. Graceful degradation

When a transport cannot carry the complete payload, the system should degrade by semantic value:

`intent → minimal context → reference → content`

not by randomly truncating arbitrary bytes.

For example, an SOS may remain useful even when photo/video cannot be delivered.

## 13. Energy- and airtime-aware policy

Future constrained transports should be able to expose estimated cost or capability metadata, for example:

- estimated bytes;
- estimated airtime;
- estimated energy class;
- expected latency class;
- reliability class;
- maximum payload size;
- store-and-forward capability.

This metadata belongs at the transport/provider boundary. It should not leak provider-specific assumptions into core capabilities.

## 14. Human attention is also a scarce resource

The same principle applies to user notifications. Prefer concise, actionable state transitions over repeated noisy alerts.

A user should receive one meaningful change notification rather than a stream of transport-level retries.

## 15. Separation of protocol, implementation, and policy

Reticulum's distinction between protocol concepts and particular implementations is useful as a design discipline:

- core semantic contracts should be technology-neutral;
- transport implementations should be replaceable;
- application policy should remain above transport;
- deployment/runtime choices should not redefine capability meaning.

Janavani should preserve this separation even when one deployment uses Reticulum, another uses Internet messaging, and another uses a future transport.

## 16. What Janavani should not adopt automatically

The research does **not** justify automatically adopting:

- Reticulum as Janavani's universal network layer;
- a public-domain/proprietary split modeled on another project;
- claims that all centralized infrastructure is inherently invalid;
- a single cryptographic identity model for every Janavani surface;
- radio/mesh-specific constraints in ordinary web workflows;
- unverified performance or security claims from project prose as Janavani requirements.

These must remain separate engineering decisions based on Janavani's requirements, legal constraints, threat model, and deployment evidence.

## 17. Recommended Janavani architecture evolution

Add a provider-neutral **Constrained Transport Contract** behind the existing delivery boundary.

Conceptual shape:

```text
Capability
   ↓
Semantic Operation / Message
   ↓
Policy + Authorization + Consequential Gate
   ↓
Transport Selection Metadata
   ↓
Provider-neutral Delivery Contract
   ├── Internet adapter
   ├── Messaging adapter
   ├── Reticulum adapter (optional)
   ├── LoRa/mesh adapter (optional)
   └── Future adapters
```

The selection layer may choose different representations for different transports while preserving semantic equivalence and provenance.

## 18. Design maxim

**Transmit intent first. Reference context. Move content only when necessary. Tell the truth about time.**
