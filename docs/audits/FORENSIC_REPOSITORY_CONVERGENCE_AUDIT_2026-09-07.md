# JANAVANI — FORENSIC REPOSITORY CONVERGENCE AUDIT

**Date:** 2026-09-07  
**Scope:** `main` repository tree and known parallel product branches  
**Purpose:** Establish one canonical product/runtime while preserving historical material under archive-first governance.

## Executive finding

The repository is still a **multi-generational codebase**, not a clean single-generation application. The forensic tree confirms three distinct implementation eras:

1. **Current root runtime** — canonical FastAPI/API, Python capability adapters, canonical Rust core, current Dioxus web client.
2. **`janavani_v2/`** — historical/parallel Rust + Dioxus + Python omnichannel stack.
3. **`janavani_v3/`** — historical/experimental Rust + Dioxus + Python stack.

The v2/v3 trees must not be merged into the active runtime. They are evidence sources only and should be archived after dependency/feature extraction is demonstrably complete.

## Confirmed duplication / collision classes

### P0 — Multiple application generations

Confirmed:
- root `src/web/canonical_app.py`
- compatibility `src/web/app.py`
- legacy `src/web.py`
- `api/agent_api.py`
- `src/web_mvp/main.py`
- historical `janavani_v2/src/web/app.py`
- historical `janavani_v3/src/web/app.py`

The historical audit records already identify repeated FastAPI/Flask definitions and repeated application/router construction in older runtime material. The current canonical entrypoint is the only runtime target for the deployed API.

**Decision:** one active API runtime; legacy app implementations are migration/archive material.

### P0 — Multiple product/client implementations

Confirmed:
- current `src/web_dioxus/`
- historical `janavani_v2/src/web_dioxus/`
- historical `janavani_v3/src/web_dioxus/`
- Python `src/web_mvp/` prototype
- multiple channel adapters/bots

**Decision:** `src/web_dioxus/` is the current WebApp candidate. Do not revive v2/v3 clients as competing products.

### P0 — Multiple domain model generations

Confirmed active root layers include:
- `src/core/civic_case.py` — canonical Python compatibility/application model
- `crates/janavani-core/src/civic_case.rs` — canonical Rust domain model
- empty placeholder `src/domain/*` files
- historical v2/v3 Rust domain/application implementations

**Decision:** Rust remains the canonical domain runtime direction. Python root models remain only where required by current adapters until migrated behind stable contracts. Empty placeholder domain/model modules are not product implementations and should be retired/archive-cleaned after import verification.

### P1 — Multiple storage paths

Confirmed:
- canonical repository boundary: `CivicCaseRepository`
- PostgreSQL provider
- Supabase provider adapter
- SQLite evidence/document providers
- local artifact blob provider
- S3 artifact provider
- legacy JSONL complaint/rating storage
- CSV authority data

**Decision:** provider multiplicity is acceptable where it is behind explicit provider contracts. Competing *business-level* storage paths are not. Case persistence must use `CivicCaseRepository`; legacy JSONL is migration/archive material only.

### P1 — Multiple document-generation paths

Confirmed:
- canonical document contract/artifact service/renderers
- `complaint_builder.py`
- legacy complaint adapter
- `generate_pdf.py`
- `pdf_generator.py`
- legacy v2/v3 document engines/renderers

**Decision:** one canonical document capability. Legacy adapters may remain temporarily only to migrate consumers.

### P1 — Multiple workflow/state engines

Confirmed:
- canonical `CivicCase` lifecycle
- `src/conversation/` Telegram state machine
- `src/engine/` workflow scaffolding
- `src/workflow/` workflow scaffolding
- historical v2/v3 workflow engines

**Decision:** interface conversation state may exist at the edge, but civic lifecycle truth belongs to canonical Case. `src/engine`/`src/workflow` must not become a second civic lifecycle authority.

## Parallel development decision

**Approved:** WebApp and Telegram should be developed in parallel.

**Constraint:** parallel development means two presentation adapters consuming the same canonical capabilities—not two independent product implementations.

### Shared implementation spine

```text
                 Canonical Janavani
                       Core
                        |
          +-------------+-------------+
          |             |             |
         Case       Authority      Evidence
          |             |             |
          +-------------+-------------+
                        |
                    Document
                        |
                Review / Consent
                        |
                  Submission
                        |
                 Tracking / Outcome
                   /           \
               WebApp       Telegram
```

WebApp and Telegram may differ in UX, transport, and interaction style. They must not independently implement Case semantics, authority resolution, document truth, consent semantics, or submission state.

## Identity finding

The repository already has a provider-neutral identity foundation (`ExternalIdentity`, `IdentityAdapter`, `Principal`, `IdentityContext`) and a separate authorization kernel. The remaining critical gap is binding trusted interface authentication to those abstractions at the HTTP/API boundary. A user-controlled `actor_id`/`created_by` value must never be treated as authentication.

## Archive-first disposition plan

Do **not** delete v2/v3 yet.

Before deletion/archive compaction, produce evidence for:

1. active imports from v2/v3 are zero;
2. required unique features have been extracted or consciously parked;
3. tests covering retained behavior exist in current root;
4. deployment manifests reference only canonical runtimes;
5. no current documentation identifies v2/v3 as executable canon;
6. archive integrity/checksum evidence exists.

After those gates, move whole generations to a clearly labelled historical archive or remove only with explicit evidence and recovery reference.

## Current canonical product target

The first vertical slice is:

**Problem → Case → Authority → Evidence → Document → Review → Consent → Submission preparation → Tracking → Follow-up → Outcome**

The immediate engineering goal is not to activate every historical capability. It is to make this slice real and reusable across WebApp and Telegram.

## Verification limitations

This audit is based on the GitHub repository tree, code-search evidence, known branch comparisons, and current architecture documents. It does not claim a successful local full test run where the execution environment cannot run the repository test suite.

## Status

- Forensic audit: **COMPLETE — initial repository-wide structural pass**
- Canonical runtime decision: **LOCKED**
- WebApp + Telegram parallel convergence: **APPROVED**
- v2/v3 deletion: **NOT YET AUTHORIZED**
- Identity/API ownership boundary: **NEXT P0**
