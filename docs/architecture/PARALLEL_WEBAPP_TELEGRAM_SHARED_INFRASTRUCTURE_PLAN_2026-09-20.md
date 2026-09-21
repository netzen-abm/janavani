# Parallel WebApp + Telegram + Shared Infrastructure Execution Plan

## Decision

From this point Janavani is developed on three parallel tracks:

1. **Shared infrastructure / capability kernel** — the canonical source of business, identity, authorization, consent, persistence and audit semantics.
2. **WebApp** — a thin independent access surface over the canonical API.
3. **Telegram** — a thin independent conversational access surface over the same capabilities.

A surface may fail without taking down the other surfaces. Neither surface may become a hidden owner of domain logic.

## Shared vertical slice

The first jointly shipped slice is:

```
Citizen identity
    ↓
Create Case
    ↓
Case ownership
    ↓
Evidence / document references
    ↓
Review
    ↓
Explicit consent
    ↓
Submission preparation
    ↓
Tracking / follow-up
```

External submission remains behind the canonical SubmissionCapability and explicit approval/consent gates.

## WebApp contract

WebApp responsibilities:

- presentation;
- browser/session UX;
- calling canonical API endpoints;
- displaying Case/document/review state;
- never trusting a browser-supplied actor ID;
- never implementing its own Case persistence;
- never implementing its own authorization rules.

The thin adapter is `src/web_mvp/services/api_client.py`.

Identity is carried as a verified assertion and is consumed by the canonical HTTP identity boundary.

## Telegram contract

Telegram responsibilities:

- Telegram update handling;
- conversation state;
- keyboards/buttons;
- Telegram-specific rendering;
- Telegram file transport.

Shared responsibilities remain in `src/capabilities`, repositories and policy infrastructure.

Telegram already creates canonical Cases through `CivicCaseCapability`; this path must remain the reference implementation rather than being replaced by a Telegram-specific case engine.

## Shared infrastructure priorities

### P0

- Provider-neutral repository contracts.
- Canonical PostgreSQL implementation.
- Principal propagation.
- Authorization/action registry.
- Consent and approval gates.
- Atomic Case/Consent/Submission transactions.
- Evidence/document ownership.
- RLS and cross-user security tests.
- CI as authoritative verification.

### P1

- Capability registry/versioning.
- Shared identity lifecycle.
- Purpose-bound consent.
- Permission lifecycle.
- Artifact/blob abstraction.
- Audit/observability.
- Idempotency and correlation IDs.
- Runtime/deployment contract.

### P2

- Additional access surfaces.
- Mobile.
- WhatsApp/Messenger.
- Mini App.
- DApp/Web3 where justified.

## Parallel delivery rule

WebApp and Telegram may advance while security work continues, but neither may bypass the canonical security boundaries.

Allowed in parallel:

- UI/UX;
- conversation UX;
- API adapters;
- rendering;
- non-sensitive local state;
- contract tests;
- capability integration.

Not allowed as shortcuts:

- direct database access from surfaces;
- surface-specific authorization;
- surface-specific Case models;
- arbitrary actor IDs;
- bypassing consent;
- automatic consequential submission;
- copying capability business logic into adapters.

## Definition of done

The first parallel vertical slice is complete when:

- Web and Telegram can create the same canonical Case type.
- Each surface has an independent runtime lifecycle.
- Each surface uses the same capability authorization.
- Ownership is enforced identically.
- Evidence/document references use shared infrastructure.
- Review and consent use shared infrastructure.
- PostgreSQL persistence is provider-neutral behind repository contracts.
- Cross-user negative tests pass.
- CI proves the shared contracts.
- A failure in Telegram does not prevent the WebApp from operating, and vice versa.

## Current implementation checkpoint

- Telegram → canonical Case capability: **implemented**.
- Telegram → shared generation/capability composition: **implemented**.
- Canonical Web API → shared Civic Case capability: **implemented**.
- WebApp thin API client: **implemented**.
- Web identity assertion boundary: **implemented**.
- Web/Telegram shared contract tests: **existing foundation + expansion in progress**.
- Live PostgreSQL/RLS gate: **not yet passed**.
- Production Web runtime verification: **not yet complete**.

## Engineering rule

Build the surfaces in parallel, but make the infrastructure the rate-limiting authority. If a feature cannot safely use the shared contract, fix the shared contract before adding a surface-specific workaround.
