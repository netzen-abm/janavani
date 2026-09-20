# Telegram + WebApp Branch Forensic Audit — 2026-09-20

## Scope

Audited the repository branch inventory and compared the principal Telegram/WebApp/shared-infrastructure branches against `main`.

Repository: `netzen-abm/janavani`
Authoritative branch: `main`
Main SHA at audit: `f09464ff24b6e35b21964b3d73d6effcd9b97d52`

## Branch inventory

The repository currently exposes **249 branches**. They are predominantly historical audit/chore/docs/feature/refactor/test branches. Many are superseded generations or duplicate snapshots.

High-confidence branch families:

- Telegram: `feat/telegram-*`, `feat/uow-telegram-*`, `refactor/telegram-*`, `integration/telegram-*`
- WebApp: `feat/webapp-*`, `feat/web-*`, `refactor/web-dioxus-*`
- Shared spine: `feat/shared-*`, `feat/case-capability-*`, `feat/product-vertical-slice-*`
- Legacy generations: `janavani_v2`, `janavani_v3`
- Historical release/prototype: `release/mvp-v0.1`, `develop/v0.2`
- Security/audit/chore branches: numerous completed/superseded snapshots

No branch was deleted during this audit. The repository rule remains: **archive/evidence first, delete only after dependency and runtime evidence.**

## Telegram branch findings

Compared with main:

| Branch | Ahead | Behind | Finding |
|---|---:|---:|---|
| feat/telegram-preview-canonical-case | 0 | 678 | Fully superseded snapshot |
| feat/telegram-consent-capability-convergence-2026-09 | 10 | 374 | Small historical delta; review useful commits only |
| feat/telegram-shared-capability-migration | 26 | 953 | Historical migration generation; do not merge wholesale |
| feat/uow-telegram-composition-convergence | 20 | 764 | Historical UoW composition generation |
| feat/uow-telegram-composition-v2 | 1 | 761 | Superseded single-step variant |
| refactor/telegram-composition-case-repository | 5 | 760 | Historical repository-composition refactor |

Canonical Telegram runtime remains `src/bot_telegram.py`. Surface orchestration must consume shared capabilities.

Critical remaining convergence item: Telegram identity is inconsistent in active code (`tg-session-<id>` vs `telegram:<id>`). This must be resolved through one adapter before cross-surface case ownership is considered complete.

## WebApp branch findings

| Branch | Ahead | Behind | Finding |
|---|---:|---:|---|
| feat/web-civic-action-composition | 3 | 608 | Useful composition delta; main already contains newer architecture |
| feat/webapp-authority-evidence-vertical-slice | 27 | 957 | Historical vertical-slice generation; selectively mine, do not merge wholesale |
| feat/webapp-civic-action-workspace | 11 | 957 | Historical workspace generation |
| refactor/web-dioxus-sos-adapter | 16 | 247 | Useful SOS boundary history; mostly superseded |
| refactor/web-dioxus-sos-adapter-clean | 8 | 247 | Intermediate cleanup |
| refactor/web-dioxus-sos-adapter-clean-v2 | 0 | 225 | Fully superseded |

Canonical Web API assembly remains `src/web/canonical_app.py`; canonical Web client candidate remains `src/web_dioxus/`.

## Shared-spine findings

The following branches are historical snapshots rather than merge targets:

- `feat/shared-civic-capability-spine`
- `feat/shared-civic-capability-spine-2`
- `feat/shared-civic-capability-spine-3`
- `feat/shared-civic-case-contract`
- `feat/shared-evidence-authority-document-spine`
- `feat/product-vertical-slice-convergence`
- `feat/case-capability-convergence-4`

The architectural substance is already represented on main. The correct strategy is selective commit/file mining, not branch-wide merging.

## Code hygiene decision

The maintainability ceiling is now **180 lines per active source file**.

The first remediation pass split:

- Web civic-case request/response models
- Web civic-case dependency composition
- Web document routes
- Web lifecycle routes
- Web civic-case routes
- shared provider composition
- shared capability composition

The public composition facade is intentionally kept thin.

Historical/archived generations remain outside the active maintainability target. They are retained for provenance and rollback evidence.

## Cleanup policy

### Keep active

- `src/bot_telegram.py`
- `src/conversation/`
- `src/capabilities/`
- `src/identity/`
- `src/platform/composition.py`
- `src/web/canonical_app.py`
- `src/web/civic_case_*.py`
- `src/web_dioxus/`
- `src/storage/`
- `src/documents/`

### Archive / retire after evidence

- `janavani_v2/`
- `janavani_v3/`
- obsolete Web prototype generations
- obsolete Telegram webhook generations
- superseded document-generator generations
- obsolete POC API paths

These must not be deleted merely because a newer implementation exists. Each candidate needs dependency, runtime, deployment, test, unique-value, replacement, and archive evidence.

## Next convergence order

1. Introduce one canonical Telegram identity adapter and migrate all Telegram commands/steps to it.
2. Migrate Telegram `/search` to the shared Authority capability.
3. Complete Web identity/session assertion flow.
4. Complete the shared Case → Evidence → Authority → Document → Review → Consent vertical slice on both surfaces.
5. Add cross-surface negative authorization tests.
6. Then archive superseded branch/file generations.

## Definition of done

Web and Telegram are complete for this slice only when:

- both create/read the same canonical Case contract;
- neither owns business logic or direct persistence;
- both use the same identity/authorization semantics;
- both support evidence, authority, document, review and consent;
- external submission remains explicitly gated;
- one surface can fail without disabling the other;
- CI proves cross-surface contract and ownership isolation;
- active source files remain ≤180 lines unless a documented exception is justified.

