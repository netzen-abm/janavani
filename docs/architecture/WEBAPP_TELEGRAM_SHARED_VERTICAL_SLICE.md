# WebApp + Telegram Shared Civic Vertical Slice

## Purpose

Build the WebApp and Telegram Bot together as independent access surfaces over the same Janavani capabilities.

The surfaces must not own separate civic business logic.

## Canonical flow

Citizen input → Case → structure facts/claims → authority/jurisdiction → evidence → document → review/correction → approval/consent → submission preparation → acknowledgement/tracking → follow-up/escalation → outcome.

## Surface contract

- WebApp: browser UX and API adapter only.
- Telegram: conversation UX and Telegram adapter only.
- Canonical domain: `src/core` / Rust core as applicable.
- Shared capabilities: `src/capabilities`.
- Persistence: repository contracts and provider adapters.
- Identity: canonical identity boundary; adapters must never trust a user-supplied actor ID.
- AI: optional capability selected by the citizen; AI output is never automatically a verified fact.

## Current execution target

1. Make both surfaces create/read the same canonical Civic Case representation.
2. Make both surfaces attach evidence/document references through shared capabilities.
3. Implement review → explicit consent → submission preparation consistently.
4. Keep actual external filing behind destination, identity, consent and submission-adapter gates.
5. Add cross-surface contract tests so a case created through one surface can be continued through another when identity policy permits.

## Explicit non-goals

- No duplicate Web-specific or Telegram-specific case engines.
- No provider-specific domain model.
- No automatic government submission.
- No blanket AI authorization.
- No central collection of sensitive citizen evidence merely to support the UI.

## Definition of done for this slice

- Same canonical case lifecycle is observable from WebApp and Telegram.
- Ownership/authorization is enforced identically.
- Repository persistence is provider-neutral.
- Document generation is a shared capability.
- Tests cover both adapters against the shared contract.
- CI/deployment evidence exists before merging to `main`.
