# JANAVANI — Branch / PR Convergence + Identity / Consent Audit

**Date:** 9 September 2026  
**Repository:** `netzen-abm/janavani`  
**Base:** `main` at `922e55d2d26649050ca620595ad988a4bdce39b8`

## Purpose

Perform the next convergence pass after the canonical runtime/storage verification. This audit checks whether active branches or open PRs contain current work that should be merged, extracted, archived, or left untouched, and verifies the current canonical Identity + Consent boundaries.

## Convergence findings

### 1. Open PR inventory

The repository currently exposes these open PRs:

- PR #49 — `chore(docs): archive stale standalone CLI guide`
- PR #47 — `chore(repo): archive obsolete HF translation test`
- PR #40 — `Security: harden authentication and authorization boundary`
- PR #33 — `docs: establish architecture authority and truthful verification model`
- PR #25 — `security: enforce admin zero-access privacy boundary`

These PRs are not treated as automatic merge candidates. Their descriptions refer to work from earlier repository generations and must be evaluated against current `main` before any merge/closure/deletion action.

### 2. Consent generation convergence

PR #83 is already merged and is the canonical historical integration point for the current Consent domain boundary. Its merged commit is `61e6ac5b7a274ef8298b574c6777189232ad2d97`.

Older consent branches such as `feat/canonical-consent-domain-boundary-v3` and `feat/postgres-consent-provider` are stale relative to current `main` and contain no commits ahead of `main` according to the repository comparison. They are therefore not current implementation sources.

The current `main` contains:

- `src/core/consent.py` — canonical Consent domain object.
- `src/storage/repositories/consent.py` — provider-neutral ConsentRepository and in-memory reference implementation.

Consent is independently owned; Case persistence must not manufacture consent records from Case references.

### 3. Identity convergence

The current `main` contains a shared identity boundary under `src/identity/` including:

- `principal.py`
- `context.py`
- `adapter.py`
- `external.py`
- `http_assertion.py`

`Principal` is the normalized caller representation. Its `principal_id` is explicitly opaque and must not contain direct identifiers such as phone numbers, email addresses, Telegram identifiers, or equivalent identifying values.

`IdentityContext` carries the resolved Principal and request metadata into shared capability execution. Adapter authentication remains separate from identity normalization and authorization.

The current implementation is therefore the canonical Identity boundary for ongoing convergence. No parallel Identity generation should be introduced merely to satisfy the checklist.

## Architectural decision

**Do not merge stale branches merely because they contain identity/consent-related names.** Current `main` already contains the canonical Python Identity and Consent boundaries, and Consent has already passed through the canonical merge path.

The remaining P0 work is not another domain-generation rewrite. It is runtime enforcement and integration:

1. bind Identity + Consent to capability authorization and consequential-action policy;
2. connect those contracts to the Case → Evidence → Authority → Document → Review vertical slice.

## Archive-first rule

No branch or PR is deleted by this audit. A stale branch is not evidence that its historical content is disposable. Any future cleanup must establish:

- no active runtime dependency;
- no unique required implementation;
- no irreplaceable historical information;
- replacement/canonical location identified where applicable;
- tests/evidence preserved where useful;
- archive location and reason recorded.

## Verification boundary

This audit does **not** claim:

- live Render/Vercel runtime verification;
- production database activation;
- production RLS readiness;
- full ecosystem implementation completion;
- clean repository-wide static linting.

Those remain separate gates in the Master Checklist.

## Result

**Branch/PR convergence:** audit completed; no stale branch is promoted into `main` solely on naming or historical intent.  
**Identity:** canonical current boundary confirmed.  
**Consent:** canonical current boundary confirmed; historical duplicate generations are not current authorities.  
**Next implementation frontier:** Identity/Consent runtime enforcement followed by the complete Case → Evidence → Authority → Document → Review slice.
