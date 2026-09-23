# JANAVANI — CANONICAL AGENT PLATFORM CONTRACT

**Status:** ARCHITECTURE CONTRACT — INTEGRATION FOUNDATION

The Agent Platform is a provider-neutral orchestration boundary for the wider Janavani ecosystem. It does not become a dependency of ordinary non-agent civic workflows.

## Canonical path

```text
Agent
  |
  v
Agent Gateway
  |
  +--> Canonical Authorization
  +--> Scoped Execution Policy
  +--> Capability Data Scope
  +--> Canonical Consent
  +--> Consequential Operation Gate
  |
  v
Shared Capability
  |
  v
Provider / Persistence Adapter
```

The gateway composes existing security controls; it must not introduce a parallel authorization or consent implementation.

## Shared capability rule

Agents orchestrate canonical Case, Evidence, Authority, Document, Consent, Submission and Tracking capabilities. They do not re-implement their semantics.

The same capability must remain independently consumable by WebApp, Telegram, Android, iOS, WhatsApp, Messenger, DApp and future surfaces.

## Identity

Human principal, agent, execution/run and provider/service identities are separate concepts. Agent identity never substitutes for citizen identity.

Agents must not receive unrestricted production database credentials when a scoped capability interface exists.

## Data and privacy

Agent execution is purpose-bound, minimum-data and provider/processing-mode scoped. Personal or sensitive citizen content must not be copied into unrestricted agent memory by default.

## Consequential actions

Consequential operations must pass the canonical consequential gate and required explicit approval. The system must distinguish prepared, approved, attempted, acknowledged and unknown outcomes.

## Failure isolation

Model, agent or provider failure must not disable unrelated civic capabilities.

## Production gaps

The repository still requires a canonical agent registry, durable agent/run identity, model-armor boundary, long-running runtime/checkpoint store, memory policy/storage, re-authorization after paused runs, and production security/privacy evidence before autonomous production execution.
