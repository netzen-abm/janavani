# Janavani Shared Platform Infrastructure

**Status:** FOUNDATION / IMPLEMENTATION  
**Date:** 25 August 2026

## Purpose

This document records the shared infrastructure skeleton introduced during repository convergence. It is intentionally paired with the implementation.

Janavani is a capability-first ecosystem with independent access surfaces. The shared platform provides stable contracts and reusable infrastructure; it must not turn one interface into a runtime dependency of another.

**Important terminology:** "optional" describes **user activation/participation**, not whether the ecosystem possesses the capability. A capability may be implemented and available to the ecosystem while a particular user chooses not to enable or use it. User choice must not remove the capability from the system or make it unavailable to other users.

The canonical architecture places independent interfaces above shared Janavani capabilities and identifies `src/adapters/` as the external integration layer, with domain, workflow, service, document and storage layers underneath.

## Initial foundation

`src/platform/` is a dependency-light extension point containing:

- `contracts.py` — channel-neutral capability, transport, storage and AI-provider contracts;
- `registry.py` — small capability registry for runtime resolution;
- `storage.py` — provider-neutral durable storage contract;
- `cache.py` — provider-neutral transient-cache contract;
- `analytics.py` — provider-neutral aggregate-telemetry contract;
- `__init__.py` — package boundary.

The registry and tests must import through the `src.platform` package boundary. This avoids an import collision with Python's standard-library `platform` module when the repository is executed from its root.

This is still a foundation, not a claim that the full platform infrastructure is implemented.

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

## Capability availability versus user activation

The ecosystem-level model is:

```text
Capability exists in Janavani
          |
          +---- available to eligible users
          |
          +---- user may enable/use it
          |
          +---- user may decline/disable it
          |
          +---- unrelated capabilities continue working
```

Therefore these terms must be distinguished in code, APIs and documentation:

- **Available:** capability is implemented and exposed by the ecosystem.
- **Enabled:** capability is active for a particular user/account/device according to policy.
- **Used:** user has invoked the capability for a specific task.
- **Unavailable:** capability cannot currently execute because implementation, configuration, permission, transport, provider or service health prevents execution.
- **Degraded:** capability remains present but some execution path/provider is unavailable.

A user's choice not to use AI, Web3, mesh, blockchain, a messaging channel or another feature must **not** be interpreted as the capability being absent from Janavani.

## Failure isolation

A capability result has an explicit status and optional error code. Implementations must define degraded behavior where an execution path, provider or transport is unavailable.

A transport outage must not become a domain outage.

An AI-provider outage must not become a basic civic-workflow outage.

A storage-provider migration must not require rewriting interfaces.

A DApp/Web3 integration must not become a mandatory dependency for Web, Android, iOS or messaging surfaces merely because those technologies are present in the ecosystem.

## User-choice model

User choice is a policy/permission layer above capability availability.

The implementation must never remove a shared capability merely because one interface or user has not selected it.

## Adapter model

The platform is intended to support independently replaceable adapters for Web/API, Android, iOS, Telegram Bot, Telegram Mini App, WhatsApp, Messenger, DApp/Web3, future resilient transports, storage providers, AI/model providers, document renderers and government/external integrations.

An adapter translates its native protocol into a stable Janavani contract. It must not copy the underlying domain implementation.

## Storage, cache and analytics convergence

The infrastructure boundaries are intentionally separated by semantics:

```text
Durable persistence
    -> src.platform.storage.StorageAdapter
    -> provider adapter, currently Supabase

Transient state
    -> src.platform.cache.CacheAdapter
    -> provider adapter, currently Redis

Aggregate telemetry
    -> src.platform.analytics.AnalyticsAdapter
    -> provider adapter, currently Redis
```

The Redis cache adapter is implemented in `src/storage/redis_cache_adapter.py`. The existing transient cache implementation remains temporarily available in `src/storage/cache.py` only for migration compatibility.

The Redis analytics adapter is implemented in `src/storage/redis_analytics_adapter.py`. The existing `PrivacyPreservingAnalytics` implementation remains temporarily available while consumers are traced and migrated.

Analytics must remain aggregate-only. No actor IDs, IP addresses, request identifiers or other identifying dimensions may be introduced merely for convenience.

The Supabase provider remains behind `src/platform/storage.py` through `src/storage/supabase_adapter.py`. Provider SDK access must remain inside the provider adapter.

## Deployment convergence

The canonical web assembly is `src.web.canonical_app:app`. `src.web.app` remains a compatibility import that delegates to the canonical assembly and must not accumulate new business logic. Deployment configuration is therefore expected to reference the canonical assembly directly rather than the compatibility module.

## Scope boundary

This foundation does **not** yet implement service discovery, distributed messaging/event bus, authentication/identity provider, authorization/policy engine, persistent registry, health aggregation, observability, secrets management, queues, concrete decentralized adapters, or full platform orchestration.

Those should be added only as evidence-driven shared infrastructure, with contracts, tests and documentation in the same change.

## Relationship to existing layers

The current architecture assigns external translation to `src/adapters/`, workflow orchestration to workflow/engine layers, domain rules to `src/domain/`, application/integration services to `src/services/`, documents to `src/documents/`, storage to `src/storage/`, and platform configuration to `src/core/`.

`src/platform/` therefore must remain a **small infrastructure-contract layer**, not a second copy of those responsibilities.

## Archive-first rule

No historical implementation is deleted merely because the shared skeleton exists. Existing implementations must be traced, migrated, tested and documented before archival or deletion decisions.

## Completion discipline

This foundation progresses through:

`DESIGNED → IMPLEMENTED → FUNCTIONAL → TESTED → SECURITY-VERIFIED → PRIVACY-VERIFIED → PRODUCTION-READY`

The presence of these files alone is not evidence of production readiness.

## Documentation rule

Every new shared infrastructure implementation must update this document and the relevant capability/architecture documentation in the same change set.
