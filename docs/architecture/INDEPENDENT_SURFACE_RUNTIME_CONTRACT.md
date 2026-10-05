# Independent Surface Runtime Contract

## Purpose

Janavani surfaces are independently deployable access boundaries over shared,
provider-neutral capabilities. Failure of one surface must not require another
surface to start, supervise, or remain healthy.

## Canonical runtimes

| Surface | Canonical bootstrap | Ownership |
|---|---|---|
| Web/API | `src.web.canonical_app:app` | Web/API deployment |
| Telegram | `src/bot_telegram.py` → `main()` | Telegram deployment |

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

The Web/API deployment path is explicit in `Dockerfile`, `Procfile`,
`entrypoint.sh`, `render.yaml`, and `pyproject.toml`.

Telegram has a canonical bootstrap and shared composition boundary, but this
repository does not yet contain an equivalent dedicated production deployment
manifest for Telegram. That is an explicit remaining deployment-conformance
gap, not a reason to couple Telegram to the Web runtime.

## Refactoring rule

Do not split shared composition merely to satisfy file-size targets. Split only
where a boundary of runtime ownership, trust, persistence, provider dependency,
change, or independent reuse is created. Preserve cohesive orchestration when
splitting would duplicate or weaken its invariant.
