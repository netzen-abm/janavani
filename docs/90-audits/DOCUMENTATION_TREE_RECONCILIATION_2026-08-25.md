# Documentation Tree Reconciliation — 2026-08-25

**Status:** Active audit  
**Authority:** `docs/DOCUMENTATION_INDEX.md` remains LOCKED as the documentation organisation standard.

## Findings

The repository already has a locked documentation authority map defining `docs/` as the current documentation area, `planning/` as active engineering contracts/specifications, and `archive/` as historical/superseded material. It also requires dated audits to remain evidence rather than silently overriding canonical documents.

A proposed numbered documentation taxonomy exists in `docs/DOCUMENTATION_STRUCTURE.md`. It is treated as a migration target/supporting document only; it does not supersede the locked index.

`docs/90-audits/` currently contains the new document-renderer convergence audit. A storage convergence audit has now been added there. This demonstrates that dated implementation audits can be grouped without moving the locked canonical documents prematurely.

The repository contains extensive architecture/runtime/documentation audits in `docs/`, while `planning/` contains active contracts such as privacy, database and document contracts. These should not be mass-moved until their inbound references and authority relationships are individually verified.

## Current rule

```text
LOCKED DOCUMENTATION INDEX
          ↓
canonical documents
          ↓
supporting contracts/specifications
          ↓
execution records
          ↓
dated audits
          ↓
archive / historical evidence
```

## No blind migration

A document may be relocated only after:

1. full-content review;
2. duplicate/overlap comparison;
3. authority classification;
4. repository reference search;
5. link/reference migration plan;
6. archive-first preservation where superseded;
7. verification that the new location does not create a second authority.

## Current discrepancies to track

- `docs/DOCUMENTATION_CLEANUP_REGISTER.md` was referenced in earlier convergence notes but is not present at that path on the current branch. Do not treat it as an active artifact until recreated deliberately.
- `docs/DOCUMENTATION_STRUCTURE.md` exists and is useful as a target taxonomy, but must remain subordinate to `docs/DOCUMENTATION_INDEX.md`.
- Historical implementation trees `janavani_v2/` and `janavani_v3/` contain documentation that must remain clearly historical/parallel until their capabilities are migrated or explicitly rejected.

## Decision

The current cleanup phase will **organize by authority and purpose before physically moving files**. This avoids creating another documentation generation while the repository is being cleaned.

No historical documentation is deleted merely because it is obsolete.
