# JanaVani Capability-First Rule

## Core principle

**Every reusable function, feature, capability, tool, service, resource, and
workflow must be designed as shareable infrastructure first.**

A surface such as Telegram, WebApp, Android, iOS, WhatsApp, Messenger, DApp,
or API is an adapter/experience layer. It must consume shared capabilities
rather than own reusable business logic.

## Required dependency direction

```text
Surface
   ↓
Adapter
   ↓
Shared Use Case / Capability
   ↓
Domain Contract
   ↓
Provider Adapter
```

Providers and transports are replaceable implementations.

## Placement test

Before adding or modifying code, ask:

> Could another JanaVani surface, service, AI agent, tool, or future product
> reasonably need this behavior?

If yes, place the behavior behind a neutral shared contract.

If no, keep it in the adapter only when it is genuinely surface-specific.

## Examples

### Shared infrastructure

- Case lifecycle
- Matter classification
- Authority resolution
- Evidence handling
- Identity model
- Consent semantics
- Document drafting
- PDF/DOCX generation
- RTI workflow
- Response assessment
- Follow-up planning
- Reminder scheduling
- Escalation graph
- Outcome recording
- Search/indexing
- AI capability interfaces
- Audit/event model
- Persistence contracts

### Surface-specific

- Telegram `Update` parsing
- Telegram buttons/keyboards
- Telegram callback handling
- Telegram message formatting
- Telegram webhook/polling runtime
- Telegram file transport to the user
- Web browser routing/UI events
- Android/iOS native UI mechanics

## Provider freedom

No shared capability may require one vendor when an open-standard boundary can
be used.

Examples:

```text
Database capability
  → PostgreSQL provider
  → Supabase provider
  → managed PostgreSQL provider
  → self-hosted provider

Identity capability
  → OIDC provider
  → Passkey provider
  → other compatible provider

File capability
  → S3-compatible storage
  → local/object storage
  → other compatible provider

AI capability
  → local model
  → hosted model
  → model gateway
  → future provider
```

## Independence rule

Failure of one surface must not make the shared capability unusable by another
surface.

```text
Telegram down   → WebApp remains usable
WebApp down     → Telegram remains usable
Supabase down   → another compliant provider can be selected
AI provider down → non-AI capabilities remain usable where possible
```

## Plug-and-play rule

Replacing an adapter/provider should not require rewriting domain contracts.

A new provider should implement the existing contract and pass the same
capability conformance tests.

## No surface ownership of policy

A surface may collect input and render results. It must not become the
authoritative owner of:

- legal/procedural policy;
- Civic Case lifecycle;
- authority truth;
- consent truth;
- document truth;
- submission/acknowledgement truth;
- follow-up strategy.

## Document-delivery invariant

JanaVani only generates PDF/DOCX artifacts and provides them to the user for
review/download. JanaVani never sends those documents to external destinations.

Follow-up may remind the user or prepare a next document, but it may not perform
the user's external action or fabricate submission/receipt/acknowledgement.

## Migration discipline

When reusable code is discovered inside a surface:

```text
Discover
  ↓
Classify
  ↓
Extract contract
  ↓
Move/reuse implementation
  ↓
Conformance test
  ↓
Switch surfaces
  ↓
Archive legacy implementation
  ↓
Delete only after evidence
```

Do not copy mature business logic into every surface.

## Review gate

Code review should reject a new surface feature when it duplicates a reusable
capability that already exists or could reasonably be shared.

The preferred result is **one capability, many adapters**.
