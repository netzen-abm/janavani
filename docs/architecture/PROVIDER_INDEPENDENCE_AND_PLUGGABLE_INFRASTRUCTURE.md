# Provider Independence & Pluggable Infrastructure

**Status:** CANONICAL ARCHITECTURAL PRINCIPLE  
**Scope:** Janavani ecosystem infrastructure  
**Decision:** No mandatory vendor or platform dependency

## 1. Principle

Janavani must not depend completely on any single vendor, hosted platform, protocol, AI provider, database service, identity provider, storage service, messaging platform, or deployment platform.

Every infrastructure capability should be:

- **Shareable** — reusable by every Janavani surface;
- **Independent** — able to operate without another optional surface;
- **Pluggable** — replaceable through a stable capability contract;
- **Portable** — deployable in more than one infrastructure environment;
- **Composable** — usable by other capabilities without duplicating domain logic;
- **Reversible** — provider changes must not require rewriting the domain kernel;
- **User-controlled where applicable** — optional infrastructure must remain a genuine user choice.

## 2. Canonical dependency direction

```text
                 JANAVANI DOMAIN KERNEL
                         |
                 CAPABILITY CONTRACTS
                         |
               PROVIDER-NEUTRAL PORTS
                         |
        +----------------+----------------+
        |                |                |
     Provider A       Provider B       Provider C
        |                |                |
     managed          managed          self-hosted
     service          service          infrastructure
```

The dependency direction is always inward:

`Surface -> Adapter -> Capability Contract -> Domain`

Never:

`Domain -> Vendor SDK`

## 3. PostgreSQL decision

PostgreSQL is the canonical relational database standard for Janavani durable relational data.

PostgreSQL is a standard, not a vendor lock-in decision.

The Civic Case domain must depend on a repository contract. Database providers implement that contract.

Supported deployment choices may include, subject to verification:

- Supabase PostgreSQL;
- managed PostgreSQL from another provider;
- cloud PostgreSQL;
- self-hosted PostgreSQL;
- local PostgreSQL for development and testing.

No application capability may require Supabase-specific semantics when standard PostgreSQL semantics are sufficient.

## 4. Supabase position

Supabase remains an **optional provider**, not the Janavani platform foundation.

Supabase-specific services may be consumed through explicit adapters where they provide value, including hosted database, authentication, storage, or realtime capabilities.

Those adapters must not leak vendor-specific types or assumptions into the canonical domain contracts.

The current Supabase Civic Case provider remains behind the repository boundary and is not production-authorized until its transaction, schema, authorization, and live-environment verification gates are satisfied.

## 5. Capability matrix

| Capability | Canonical contract | Provider examples |
|---|---|---|
| Relational persistence | Repository / PostgreSQL contract | Supabase, RDS, Cloud SQL, Neon, self-hosted |
| Object storage | Artifact storage contract | S3-compatible, Supabase Storage, cloud object storage, local/self-hosted |
| Identity | Identity contract | OIDC, passkeys, Supabase Auth, other IdPs |
| Authentication | Authentication adapter | OIDC, WebAuthn/passkeys, channel providers |
| Messaging | Transport contract | Telegram, WhatsApp, Messenger, email where explicitly permitted |
| Realtime | Event/notification contract | WebSocket, SSE, Redis, provider realtime services |
| Cache | Cache contract | Redis, local cache, other compatible cache |
| AI | AI capability contract | OpenRouter, direct model providers, Genkit, local models, deterministic fallback |
| Search/RAG | Search contract | FAISS, PostgreSQL search, external/vector providers |
| Decentralized transport | Protocol adapter | Nostr, IPFS, other future protocols |
| Deployment | Runtime contract | Vercel, containers, cloud, self-hosted |

The table is architectural guidance, not a declaration that every provider is currently implemented.

## 6. No mandatory optionality

An optional provider must remain optional at runtime.

Examples:

- Telegram failure must not break the Web App.
- Supabase failure must not corrupt or redefine the Civic Case domain.
- AI unavailability must not make deterministic civic workflows impossible where a non-AI path exists.
- Web3/Nostr/IPFS unavailability must not break core civic capabilities.
- A provider credential must not become a citizen identity.

## 7. Failure isolation

Each adapter must have explicit failure semantics.

Provider failure should produce a controlled capability error, degraded mode, retryable state, or alternate provider path according to the capability contract.

It must not silently change business meaning.

For example:

`database unavailable != case deleted`

`submission provider unavailable != government rejection`

`AI unavailable != citizen request invalid`

`transport unavailable != capability unavailable`

## 8. Vendor-neutral testing

Every critical capability should have two classes of verification:

1. **Contract tests** — execute against a provider-neutral test implementation.
2. **Provider tests** — execute against each supported provider implementation.

The provider-neutral test suite is the architectural safety net that prevents vendor coupling.

## 9. Data portability

Canonical domain records must have explicit serialization and migration representations.

A provider migration must be possible without changing the domain model:

```text
Provider A
   |
   v
Canonical representation
   |
   v
Provider B
```

No provider-specific identifier should become the only canonical identity for a domain object.

## 10. Operational freedom

Janavani should be capable of operating in progressively different environments:

```text
Developer laptop
      |
      v
Local/test infrastructure
      |
      v
Managed cloud
      |
      v
Institutional/private cloud
      |
      v
Self-hosted infrastructure
```

The same capability contracts should survive these transitions.

## 11. Implementation rules

1. Do not import vendor SDKs into domain modules.
2. Keep vendor SDK imports inside adapters/providers.
3. Pass canonical domain objects across capability boundaries.
4. Do not expose vendor response objects as public domain API.
5. Keep provider configuration outside business logic.
6. Use feature flags or provider selection at composition boundaries, not throughout the domain.
7. Maintain at least one provider-neutral implementation for critical capabilities.
8. Prefer standards-based protocols over proprietary abstractions where practical.
9. Do not introduce a second abstraction when an existing canonical contract already covers the capability.
10. Archive superseded provider-specific implementations before removal.

## 12. Current implementation priority

The immediate storage sequence is:

1. retain the canonical `CivicCaseRepository` contract;
2. implement a standard PostgreSQL provider using a PostgreSQL-native driver;
3. keep the Supabase provider as an adapter;
4. establish migration tooling independent of Supabase;
5. run contract tests against local PostgreSQL;
6. run provider tests against Supabase only after live schema/RLS evidence is available;
7. make provider selection explicit and reversible;
8. deprecate overlapping legacy storage adapters only after consumer inventory and migration evidence.

## 13. Architectural test

Before accepting a new dependency, ask:

> If this vendor disappeared tomorrow, could Janavani retain its domain model and continue using the capability through another provider?

If the answer is no, the dependency is in the wrong architectural layer.

## 14. Freedom rule

**Janavani owns the capabilities. Providers merely implement them.**

No vendor owns the Janavani domain, identity model, civic case lifecycle, citizen records, capability contracts, or architectural authority.
