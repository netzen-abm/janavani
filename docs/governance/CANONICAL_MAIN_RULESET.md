# Janavani Canonical `main` Ruleset

**Status:** Canonical specification
**Scope:** `main` branch and all changes targeting `main`
**Baseline:** `baeb042fa9d4d987120367bb5b43eb9e52fec8f8`

## Purpose

`main` is the canonical Janavani integration line. It must remain buildable, reviewable, auditable, and free of unproven architectural bypasses.

## Required protection

1. Changes reach `main` through a pull request. Direct pushes are disabled except for an explicitly documented emergency procedure.
2. At least one independent review is required before merge.
3. Required CI status checks must be green before merge. The repository must require the canonical CI/security/architecture verification checks that exist on `main`; check names may be updated only when the workflow contract changes.
4. Branches must be up to date with `main` before merge when required checks depend on the exact merge result.
5. Force pushes and branch deletion on `main` are prohibited.
6. Merge commits, squash merges, or rebases may be enabled according to repository policy, but the merge method must not bypass required checks or review.

## Architectural invariants

1. `main` is the only canonical production-integration branch.
2. Access surfaces are adapters/clients. They do not become owners of shared domain state or provider-specific persistence.
3. Shared capabilities have one canonical owner and may be consumed by multiple surfaces.
4. Provider implementations sit behind provider-neutral contracts and composition boundaries.
5. Direct provider construction is allowed only inside an approved composition root/factory or provider adapter.
6. Direct database/storage access is allowed only in the storage/repository layer or a documented adapter.
7. Surface code must not select databases, construct provider clients, or bypass repository/service contracts.
8. Legacy implementations may remain only when their ownership and migration/archive status are documented; active production paths must not depend on them accidentally.
9. Archive before delete. Deletion requires evidence that there are no active imports, runtime references, deployment references, or test dependencies.
10. Optional capabilities are optional for the user, not optional for the Janavani ecosystem.
11. Privacy and safety controls are cross-cutting requirements and must not be bypassed by a surface or provider.
12. AI and Agentic AI are shared capabilities, not surface-owned business logic; consequential agent actions require policy/authorization/confirmation as applicable.

## Change requirements

Every PR targeting `main` must state:

- affected capability/surface;
- canonical owner of changed logic;
- provider/storage impact;
- migration or archive impact;
- security/privacy impact;
- test evidence;
- deployment/runtime impact when applicable.

Architecture changes must update the authoritative documentation/decision record in the same change set or explicitly reference an existing authoritative decision.

## Merge blockers

A change must not merge when it introduces:

- a new surface-owned database/provider path;
- a new direct protected-data access path;
- duplicated canonical capability logic without a documented transitional reason;
- a production path that depends on another independent access surface;
- unexplained legacy bypasses;
- secrets or credentials committed to source;
- a failing required check;
- unreviewed consequential security/authorization changes.

## Emergency procedure

An emergency change may be applied only when necessary to restore service/security and must be followed by a normal PR documenting the reason, exact diff, verification, and remediation. Emergency access must not become routine development practice.

## Verification

The actual GitHub repository Settings must enforce this specification. The repository automation can verify repository-state facts that are available to CI, but GitHub Settings remains authoritative for branch/ruleset protection.
