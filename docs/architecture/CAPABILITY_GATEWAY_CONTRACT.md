# JanaVani Capability Gateway Contract

## Status

**Architecture contract — initial composition boundary.**

## Purpose

The Capability Gateway is the shared composition boundary through which
independent JanaVani surfaces invoke reusable capabilities without owning the
business logic themselves.

It is not a monolith and not a vendor-specific API gateway. It is a stable
boundary between surface adapters and JanaVani capability contracts.

## Dependency direction

```text
Surface Adapter
      |
      v
Capability Gateway
      |
      v
Capability Contract
      |
      v
Domain / Use Case
      |
      v
Provider Adapter
```

## Initial capability groups

The gateway is intended to expose contracts for:

- Civic Case
- Authority and jurisdiction
- Document generation and artifacts
- RTI workflow
- Follow-up and next-action planning
- Identity
- Consent
- Evidence
- Search and directory
- AI assistance
- Notifications and reminders

A capability may be invoked by multiple surfaces and services.

## Surface independence

Supported surfaces may include:

- Dynamic Web/WebApp
- Telegram Bot
- Telegram Mini App
- Android
- iOS
- WhatsApp
- Messenger
- DApp/Web3
- API clients
- controlled AI agents

No surface is the canonical owner of a capability.

## Provider independence

The gateway must not require a particular database, AI provider, messaging
provider, cloud platform, or hosted service.

Provider selection remains behind provider contracts. A provider outage must
not require rewriting domain logic or unrelated surfaces.

## Document boundary

The gateway may request document generation and return PDF/DOCX artifacts.
It must never provide an operation that sends a generated document to an
external address.

The following are explicitly outside the document gateway contract:

- email transmission;
- postal or courier delivery;
- government portal submission;
- transmission to an authority by Telegram, WhatsApp, or another channel.

A user may independently perform those actions after download.

## Follow-up boundary

The gateway may:

- calculate a next-action recommendation;
- schedule a user-selected reminder;
- present follow-up choices;
- record user-reported outcomes;
- request generation of the next document.

It must not execute the user's external action automatically.

## AI boundary

AI may assist a capability but cannot become its source of truth merely by
being an AI model. Critical facts such as authority identity, jurisdiction,
legal procedure, delivery, acknowledgement, and resolution require
appropriate authoritative data or evidence.

Agents may call approved capability contracts. Agents must not receive
unrestricted database access merely because they are agents.

## Stateless surface principle

Surface runtimes should remain disposable. Persistent case, document,
evidence, consent, and follow-up state belongs behind shared persistence
contracts.

Cloud Run, Firebase, Telegram, or any other runtime is therefore an adapter
dependency, not the source of truth.

## Failure isolation

A failure in one surface must not cause failure in another surface.

```text
Telegram Bot down      -> WebApp continues
Mini App down          -> Telegram Bot continues
AI provider down       -> deterministic/core capabilities continue where possible
Supabase unavailable   -> provider failover/alternative remains possible
One notification path  -> case state remains intact
```

## Conformance requirement

Every adapter implementing a gateway capability must pass the capability's
provider-neutral contract tests. Surface-specific tests may add UX behavior,
but they may not redefine domain semantics.

## Implementation sequence

1. Define capability contracts.
2. Define request/response DTOs that contain no surface framework types.
3. Implement gateway composition functions.
4. Add conformance tests.
5. Connect Telegram as the first adapter.
6. Connect WebApp/Mini App without copying capability logic.
7. Add other surfaces incrementally.

The gateway remains a composition boundary, not a new location for business
logic that should belong to the underlying capabilities.
