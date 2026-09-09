# JANAVANI — Branch / PR Convergence + Identity / Consent Audit

**Date:** 9 September 2026  
**Repository:** `netzen-abm/janavani`  
**Main after this pass:** `d1d35c1ba946d361edcd2373ca993f0a9290d454`

## Result

This pass completed a targeted branch/PR convergence audit and began the P0 Identity + Consent runtime-enforcement slice.

### Branch / PR findings

The repository has many historical branches representing multiple generations. They are not treated as current implementation authorities merely because their names sound canonical.

Consent generations were compared against `main`. The merged PR #83 established the current canonical Consent domain boundary. Older consent branches are stale relative to current `main` and were not promoted.

PR #49 was found to contain useful archive-first work, but its branch was 290 commits behind current `main`. The same intended change was safely reproduced on current `main`: the stale CLI guide was copied to `docs/archive/legacy/CLI_INSTALLATION_GUIDELINES.md` with its historical content preserved, the active copy was removed, and PR #49 was closed as superseded. No historical material was intentionally discarded.

Other open PRs remain subject to separate evidence-based review; they were not merged merely because they are old security or architecture work.

## Canonical Identity

Current `main` contains the shared `src/identity/` boundary with `Principal`, `IdentityContext`, adapters and HTTP assertion handling. `Principal.principal_id` is opaque and direct identifying channel values are not intended to become principal identifiers. Identity normalization, authentication and authorization remain separate concerns.

## Canonical Consent

Current `main` contains `src/core/consent.py` and `src/storage/repositories/consent.py`. Consent is independently owned and provider-neutral. Case persistence must not manufacture consent.

The Consent object enforces required identifiers/purpose/timestamps and revoked-state metadata. `authorizes()` requires granted status plus matching purpose and scope.

## Runtime enforcement added

Added `src/access/consent.py` with:

- `ConsentRequirement` — subject, purpose and scope;
- `ConsentRepositoryReader` — minimal provider-neutral read contract;
- `require_consent()` — deterministic fail-closed enforcement;
- `ConsentRequiredError` — explicit denial when valid consent is absent.

Added `tests/test_consent_enforcement.py` covering matching granted consent, missing consent, denied consent, and scope mismatch.

This is intentionally a narrow enforcement boundary. It does not yet wire every consequential capability to Consent, does not activate PostgreSQL consent persistence, and does not claim production authorization completion.

## Verification status

Repository writes completed successfully. GitHub Actions for the final commit are not yet available in the connector response, so this pass does **not** claim CI success for these new commits.

The previously verified `main` CI evidence remains valid for its tested commit, but must not be silently reused as proof for the new changes.

## Next implementation step

Wire `require_consent()` into the first consequential shared capability — submission/delivery is the preferred target — while preserving explicit user approval and keeping authentication, authorization and consent as separate decisions.

Then continue the flagship Case → Evidence → Authority → Document → Review vertical slice.

## Archive rule

No branch deletion was performed. No stale code was deleted without an archived replacement and reason. Future branch cleanup remains evidence-driven.
