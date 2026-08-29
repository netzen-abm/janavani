# Janavani Repository Audit — 2026-08-29

## Scope

Audit the current repository state with emphasis on canonical runtime ownership, shared capability architecture, independent access surfaces, CI truthfulness, and legacy/multi-generation convergence.

## Current evidence

- Repository default branch: `main`.
- PR #38 (`refactor/case-capability-kernel`) is open and draft; it targets `main` and is mergeable, but its CI is not green.
- The canonical runtime check passed on the PR merge commit.
- Full Python validation failed during test collection because `src/conversation/steps/select_office.py` used imports such as `conversation.session` and `services.authority_service` instead of the repository package boundary `src.conversation...` / `src.services...`.
- The import defect was corrected on the working branch; a new CI run is required before treating the fix as verified.
- `run_all_tests.sh` intentionally runs the complete Python suite before the Rust/Dioxus suite.
- The repository still contains legacy/parallel surfaces including `src/web.py`, `src/web_dioxus`, `src/web_mvp`, channel implementations, and multiple storage/service layers. These remain audit/convergence candidates; no deletion is authorized merely from presence.

## Findings

### P0 — CI collection failure

The latest PR validation reached 118 collected tests but stopped on one collection error in `tests/test_telegram_select_office.py`. Root cause: a Telegram conversation step imported package modules as top-level modules. This is a concrete namespace/package-boundary defect, not a test-data problem.

Status: **fix applied; verification pending**.

### P1 — Multiple runtime generations

The source tree contains both canonical FastAPI runtime code and historical Flask/web/Dioxus/MVP generations. The canonical deployment direction is FastAPI, but legacy runtimes must remain archived/isolated until reference and deployment evidence is complete.

Status: **convergence in progress**.

### P1 — Storage ownership is still mixed

The repository contains in-memory, JSONL, Supabase, relationship/event, cache and other storage implementations. Provider-neutral repository contracts exist, but production ownership and migration are not yet fully runtime-verified.

Status: **convergence in progress**.

### P1 — Capability layers are growing faster than integration evidence

Case, Evidence, Authority, Document, AI/Agentic AI, privacy, and platform contracts exist or are under development. The main remaining risk is declaring capabilities complete before end-to-end behavior, failure isolation, provenance, and security properties are verified.

Status: **do not mark complete without executable evidence**.

### P2 — Rust/Dioxus and client surfaces

`src/web_dioxus`, Web MVP, and other access surfaces require ownership mapping and independent-runtime verification. The shared capability model should remain the boundary; clients must not become alternative business-logic owners.

Status: **audit pending**.

## Required convergence order

1. Restore green canonical Python test collection.
2. Run the full Python suite and record failures by capability.
3. Run Rust/Dioxus tests independently.
4. Reconcile runtime/deployment entrypoints.
5. Map storage ownership and migrate consumers to canonical repository contracts.
6. Consolidate document renderer/generator ownership.
7. Verify Case → Evidence → Authority → Document workflow end-to-end.
8. Integrate submission, delivery receipt, tracking and follow-up.
9. Verify privacy/safety/failure-isolation properties.
10. Only then consider deletion of archived generations.

## Architectural invariants

- Optional means user choice, not ecosystem absence.
- Every approved capability remains part of Janavani even when a user does not invoke it.
- Access surfaces are independently operable.
- Shared capabilities are reusable infrastructure first.
- Providers and technologies are adapters behind stable contracts.
- AI/Agentic AI are optional capabilities and must not become mandatory dependencies for deterministic civic workflows.
- Privacy and safety are by design and by default.
- Personal Case/Evidence data must not be sent to remote AI merely because AI exists.
- High-impact agentic actions require scoped authorization and appropriate human confirmation.
- Archive first; delete only after evidence.
- Green means verified behavior, not successful compilation alone.

## Immediate decision

Do not start broad UI expansion or additional provider integrations until the canonical Python suite is green and the Case persistence/runtime boundary is verified. Continue building shared capability infrastructure in parallel, but each new capability must carry contract, tests, integration evidence, and documentation.
