# Shared Provider Composition Convergence

## Decision

All persisted repositories used by an access surface must be selected through the shared `ProviderComposition` boundary. Surfaces may inject an already-composed repository, but they must not independently choose or instantiate a persistence provider.

The shared platform composition now covers the canonical persisted domains that already have bounded factories:

- civic case
- consent
- submission
- document review
- accountability feedback
- external channel

## Current state

`memory` remains the safe default for free/local development. Durable providers are selected only where an explicit bounded adapter exists. Document review currently supports only `memory`; requesting an unimplemented durable provider fails closed.

This does **not** introduce a PostgreSQL migration or a new generic storage layer. Durable implementation remains evidence-driven and domain-specific.

## Surface rule

The Web composition previously constructed `InMemoryConsentRepository` and `InMemoryDocumentReviewRepository` directly. Those defaults now resolve through the shared platform composition. The Web adapter can still inject explicit repositories for tests or deployments, while the default path follows the same provider plan as other surfaces.

## Submission boundary

The canonical civic-action composition now also resolves its default submission repository from the same `ProviderComposition`, preventing a hidden environment-based provider decision inside the vertical slice.

## Deferred work

Do not add durable document-review persistence merely for provider symmetry. Before adding it, establish the authoritative review lifecycle, schema, concurrency semantics, audit requirements, migration evidence, and a bounded adapter contract.
