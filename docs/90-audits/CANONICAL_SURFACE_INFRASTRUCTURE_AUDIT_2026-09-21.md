# Canonical Surface Infrastructure Audit — 2026-09-21

## Scope

Audit the current WebApp and Telegram surface composition against the canonical shared-infrastructure contract.

## Findings

### WebApp

`src/web/composition.py` now derives omitted Case, Authority and Evidence repositories from one `ProviderComposition`. Explicit repository injection remains supported for tests/deployments.

The Web submission transport remains fail-closed until a real external transport is configured.

The vertical slice receives the same provider composition, so PostgreSQL submission configuration can select the atomic Submission + Case transaction repository.

### Telegram

`src/bot_telegram.py` composes one `SurfaceCaseComposition` and exposes its canonical Case, Civic Action, Evidence, Authority, Consent and identity-link dependencies to the Telegram adapter.

Telegram-specific conversation/generation code remains an adapter concern and must not create a second domain capability graph.

## Canonical rule

A surface may own interaction state and platform-specific adapters. It must not own a competing implementation of Case, Evidence, Consent, Authorization, Submission, or persistence policy.

## Remaining audit targets

1. Search every active runtime surface for direct repository construction.
2. Search every active runtime surface for direct authorization/consent implementation.
3. Replace remaining duplicate construction paths with ProviderComposition + capability factories.
4. Keep historical generations quarantined; do not merge them wholesale.
5. Verify PostgreSQL integration tests before production provider activation.

## Branch policy

Only the nine sanctioned development roles are active. Historical refs are evidence/retirement candidates. Physical deletion requires an available GitHub ref-delete operation; refs must not be force-moved as a substitute.

## Decision

The current architecture is suitable for continued ecosystem convergence. The next work should be removal of remaining duplicate runtime construction paths, not addition of another framework.
