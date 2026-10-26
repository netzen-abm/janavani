# Independent Surface Runtime Contract

## Purpose

Janavani surfaces are independently deployable access boundaries over shared,
provider-neutral capabilities. Failure of one surface must not require another
surface to start, supervise, or remain healthy.

## Canonical runtimes

| Surface | Canonical bootstrap | Ownership |
|---|---|---|
| Web/API | `src.web.canonical_app:app` | Web/API deployment |
| Citizen WebApp | `src.webapp.main:app` (Vercel package entrypoint re-exports this app) | WebApp deployment |
| Telegram webhook | `src.web.telegram_webhook_app:app` | Independent HTTPS webhook deployment |

`src.bot_telegram.build_application()` composes Telegram handlers and shared capabilities. Its `main()` deliberately fails closed: it is not a runtime entrypoint and must never start polling. The webhook adapter initializes the same application, registers the bot webhook, durably accepts encrypted updates into PostgreSQL, and dispatches them through the bounded-retry inbox worker.
## Shared infrastructure boundary

Both surfaces may consume the shared `SurfaceCaseComposition` and canonical
capability contracts. Neither surface may create a parallel authorization,
consent, Case-ownership, protected-data, or provider-selection implementation.

## Independence requirements

1. Web/API startup must not spawn or supervise Telegram.
2. Telegram startup must not import or require the Web/API application.
3. Surface composition may be shared; surface runtime lifecycle must not be shared.
4. A surface-specific transport/provider failure must remain contained to that
   surface unless a shared dependency itself is unavailable.
5. Cross-surface continuity is achieved through canonical identity, Case and
   capability contracts—not through process coupling.
6. Deployment manifests must identify the intended surface explicitly.

## Current deployment evidence

The Web/API, citizen WebApp, and Telegram webhook entrypoints are explicit in
the active deployment configuration and tests. `render.yaml` describes three
independent services, but deliberately labels them `JANAVANI_RUNTIME_MODE=test`;
it is a non-production blueprint, not proof of a production-ready deployment.

The canonical Python webhook's production readiness still depends on actual
secret configuration, shared durable providers, least-privilege database roles,
the encrypted inbox migration, webhook-registration evidence, and cross-surface
acceptance. A deployment declaration or `/liveness` response alone is not
production evidence. The legacy polling entrypoint is retired and must remain
fail-closed.
## Refactoring rule

Do not split shared composition merely to satisfy file-size targets. Split only
where a boundary of runtime ownership, trust, persistence, provider dependency,
change, or independent reuse is created. Preserve cohesive orchestration when
splitting would duplicate or weaken its invariant.
