# Janavani Shared Platform Infrastructure

**Status:** FOUNDATION / IMPLEMENTATION
**Date:** 25 August 2026

## Purpose

This document records the shared infrastructure skeleton introduced during repository convergence. It is intentionally paired with the implementation.

Janavani is a capability-first ecosystem with independent access surfaces. The shared platform provides stable contracts and reusable infrastructure; it must not turn one interface into a runtime dependency of another.

The canonical architecture places independent interfaces above shared Janavani capabilities and identifies `src/adapters/` as the external integration layer, with domain, workflow, service, document and storage layers underneath. fileciteturn497file0L2-L2

## Initial foundation

`src/platform/` is a dependency-light extension point containing:

- `contracts.py` — channel-neutral capability, transport, storage and AI-provider contracts;
- `registry.py` — small capability registry for runtime resolution;
- `__init__.py` — package boundary.

This is a skeleton, not a claim that the full platform infrastructure is implemented.

## Shared capability contract

```text
Independent Surface
       |
       v
CapabilityRequest
       |
       v
CapabilityRegistry
       |
       v
CapabilityHandler
       |
       v
CapabilityResult
```

Clients should depend on the contract, not on another client or a provider-specific implementation.

## Failure isolation

A capability result has an explicit status and optional error code. Implementations must define degraded behavior where the underlying capability is optional or replaceable.

A transport outage must not become a domain outage.

An AI-provider outage must not become a basic civic-workflow outage.

A storage-provider migration must not require rewriting interfaces.

A DApp/Web3 integration must not become a mandatory dependency for Web, Android, iOS or messaging surfaces unless a future architectural decision explicitly establishes that requirement.

## Adapter model

The platform is intended to support independently replaceable adapters for:

- Web/API;
- Android;
- iOS;
- Telegram Bot;
- Telegram Mini App;
- WhatsApp;
- Messenger;
- DApp/Web3;
- future decentralized or resilient transports;
- storage providers;
- AI/model providers;
- document renderers;
- government/external integrations.

An adapter translates its native protocol into a stable Janavani contract. It must not copy the underlying domain implementation.

## Future technology plug-in rule

Future Web3/Web4/Web5-style technologies, decentralized identity, verifiable credentials, blockchain, Nostr, Nym, Reticulum, Freenet, new AI runtimes, new model providers and future client technologies should enter through adapters/contracts where they provide a verified capability.

The desired migration is:

```text
new technology
    -> adapter implementing existing contract
    -> capability registration
    -> policy / consent / security review
    -> tests
    -> documentation
    -> independent deployment
```

The ecosystem must not require a rewrite of existing clients to adopt a new technology.

## Scope boundary

This foundation does **not** yet implement:

- service discovery;
- distributed messaging/event bus;
- authentication/identity provider;
- authorization/policy engine;
- persistent registry;
- health aggregation;
- observability;
- secrets management;
- queues;
- caching;
- concrete storage adapters;
- concrete AI adapters;
- concrete Web3/Web5 adapters.

Those should be added only as evidence-driven shared infrastructure, with contracts, tests and documentation in the same change.

## Relationship to existing layers

The current architecture already assigns external translation to `src/adapters/`, workflow orchestration to workflow/engine layers, domain rules to `src/domain/`, application/integration services to `src/services/`, documents to `src/documents/`, storage to `src/storage/`, and platform configuration to `src/core/`. fileciteturn497file0L2-L2

`src/platform/` therefore must remain a **small infrastructure-contract layer**, not a second copy of those responsibilities.

## Archive-first rule

No historical implementation is deleted merely because the shared skeleton exists. Existing implementations must be traced, migrated, tested and documented before archival or deletion decisions.

## Completion discipline

This foundation progresses through:

`DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → PRODUCTION-READY`

The presence of these files alone is not evidence of production readiness.

## Documentation rule

Every new shared infrastructure implementation must update this document and the relevant capability/architecture documentation in the same change set.
