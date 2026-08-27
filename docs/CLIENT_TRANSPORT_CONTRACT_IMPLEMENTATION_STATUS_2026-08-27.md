# Janavani Client/Transport Contract Status — 2026-08-27

**Branch:** `refactor/case-capability-kernel`  
**Status:** DESIGN COMPLETE for permission/consent and transport boundaries; implementation mapping remains open.

## Completed in this pass

- Added `docs/PERMISSION_CONSENT_CONTRACTS.md`.
- Added `docs/TRANSPORT_ABSTRACTION_CONTRACTS.md`.
- Dioxus now has a provider-neutral client capability boundary in `src/web_dioxus/src/client_capability.rs`.
- Dioxus execution strategy now uses explicit browser observations rather than opaque device heuristics.
- Simulated decentralized provider success was removed; unconfigured providers report unavailable.
- Simulated SOS success was removed; SOS transport reports unavailable until a real adapter exists.

## Architectural decisions

1. Channels do not own civic-domain logic.
2. Capabilities consume provider-neutral contracts.
3. Permission and consent are separate from transport availability.
4. Local queue/persistence is never delivery confirmation.
5. Provider adapters do not make authorization decisions.
6. Mock/scaffold providers must never report production availability.
7. Web, Telegram Bot, Telegram Mini App, Android, iOS and DApp are independent surfaces over shared capability contracts.
8. AI, blockchain, mesh, satellite and decentralized infrastructure remain replaceable optional adapters unless a capability explicitly requires them.

## Evidence-calibrated status

| Area | Current state |
|---|---|
| Permission/consent contract | DESIGN COMPLETE |
| Transport abstraction contract | DESIGN COMPLETE |
| Dioxus client capability boundary | IMPLEMENTATION |
| Browser execution observation | IMPLEMENTATION + UNIT TESTS |
| Decentralized provider adapters | NOT CONFIGURED |
| SOS transport adapter | NOT CONFIGURED |
| Telegram shared capability adapter | IMPLEMENTATION MAPPING PENDING |
| Mini App | DESIGN |
| Android | DESIGN |
| iOS | DESIGN |
| DApp | DESIGN |

## Verification still required

- Map each capability to concrete permission enforcement code.
- Add server-side authorization enforcement and audit events.
- Implement transport adapter interfaces in the runtime layer.
- Add transport state-machine integration tests.
- Verify Dioxus build in CI.
- Verify Telegram Bot uses shared capability/API contracts rather than duplicate domain logic.
- Define and implement cross-channel identity linking only after consent contracts are enforced.
- Add failure/dependency matrix, threat model and system-wide test strategy.

## Completion rule

No item above should be marked `COMPLETE` merely because this document or a design contract exists. Completion requires implementation, tests, repository verification, applicable security/privacy review, functional verification and evidence in `docs/MASTER_TASK_CHECKLIST.md`.
