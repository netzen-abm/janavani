# WebApp Civic Action Workspace — Build Contract

## Decision
The Dynamic Web is the first active product surface. Shared capabilities remain in the platform/domain/service layers and are consumed by the WebApp through contracts. The WebApp owns presentation and interaction, not shared business logic.

## First production vertical slice

`Create Case → Understand → Authority → Evidence → Document → Review → Approve → Submit/Prepare → Track`

## Product object
A **Case** is the shared civic-action object. A case can be accessed by any authorized Janavani surface without making that surface the owner of the case.

## Capability boundaries
- Case: shared domain/service capability.
- Authority: shared government-information capability; official contact data requires provenance/verification state.
- Evidence: shared capture/provenance capability.
- Documents: shared composition/rendering capability.
- AI: optional, circumstance-based, replaceable; never the source of truth.
- Submission: explicit user approval and truthful delivery state.
- Tracking: shared lifecycle capability.
- WebApp: UI, navigation, presentation, client-side validation and API consumption.

## Non-negotiables
1. No WebApp dependency on Telegram, mobile, DApp or another client.
2. No AI requirement for the deterministic core workflow.
3. No invented government authority/address data.
4. No claim of submission/delivery without confirmed state.
5. Privacy and safety defaults remain active regardless of optional capability choice.
6. The same capability contract must be consumable by future clients.
7. Legacy implementations are archived before deletion.

## Verification gates
A feature is not considered complete until its code path, tests, API/runtime behavior and user-facing workflow are verified. POC/scaffold code must not be represented as production capability.
