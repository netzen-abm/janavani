# Transport Contract Audit — 2026-08-25

**Branch:** `refactor/document-capability-convergence`

## Decision

Introduce one channel-neutral transport boundary at `src/platform/transport.py`.

The boundary normalizes provider-native inbound events into `TransportMessage` and expresses outbound attempts as `TransportResult`. It does not own business logic, capability execution, storage, AI, document generation, authentication policy, or provider-specific domain models.

## Why

The canonical architecture requires independent Web, Android, iOS, Telegram, WhatsApp, Messenger and DApp surfaces while shared capabilities remain channel-neutral. The repository's architecture principles explicitly require interfaces to consume capability contracts and external providers to remain adapters. 

## Required semantics

### Inbound

`TransportMessage` carries only normalized transport context: transport name, message reference, conversation reference, actor reference, text, attachments and non-sensitive metadata.

Provider-specific payloads remain inside the adapter.

### Outbound

`TransportResult.status` describes the transport state. `accepted` must never be interpreted as `delivered` or `acknowledged`. Provider references and retryability are explicit.

### Failure isolation

A provider failure must remain local to that adapter/capability invocation. The transport boundary must not create a runtime dependency between Telegram, WhatsApp, Messenger, Web, mobile or DApp.

### Privacy and safety

The boundary does not require tracking identifiers. Authentication, authorization, consent, rate limits, replay protection, secret management and safety policy remain explicit concerns outside provider-specific business logic.

## Implementation status

- Contract: IMPLEMENTED
- Deterministic contract tests: IMPLEMENTED
- Telegram adapter migration: NOT YET IMPLEMENTED
- WhatsApp adapter migration: NOT YET IMPLEMENTED
- Messenger adapter migration: NOT YET IMPLEMENTED
- Delivery state integration: NOT YET IMPLEMENTED
- Legacy transport deletion: NOT AUTHORIZED

## Cleanup rule

Legacy transport generations remain until deployment/import/runtime evidence demonstrates that they are unused, their replacement is tested, and their historical implementation has been preserved in the archive.

## Architectural rule

New channels and transports should implement this boundary and capability contracts instead of introducing a new channel-specific business-logic stack.
