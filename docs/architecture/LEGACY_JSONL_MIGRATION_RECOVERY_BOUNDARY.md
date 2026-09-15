# Legacy JSONL Migration / Recovery Boundary

**Date:** 2026-09-15
**Status:** Implemented as a read-only recovery boundary

## Purpose

`database/complaints.jsonl` and `database/ratings.jsonl` are preserved historical sources. They are not runtime authorities and must not become an alternate application persistence path.

The repository now has a small, explicit migration/recovery boundary at `src/migration/legacy_jsonl.py`.

## Boundary

```text
Preserved historical JSONL
        |
        v
LegacyJsonlSource (read-only)
        |
        v
Validation / recovery report
        |
        v
Source-specific transformation
        |
        v
Canonical domain repository
        |
        v
Provider adapter (PostgreSQL/Supabase/etc.)
```

The migration layer is intentionally **not** a replacement for the canonical repository layer and is not a generic application storage adapter.

## Guarantees

- Source files are never modified by the recovery boundary.
- Empty files are valid sources.
- Invalid JSON is reported with its line number instead of being silently discarded.
- Non-object JSON records are rejected.
- Missing sources fail closed.
- Validation is deterministic and suitable for dry-run/recovery workflows.
- Transformation and persistence remain separate concerns.

## Current data state

At the time of this implementation, both preserved repository files are empty. Therefore there is no historical record requiring migration yet.

This is important: **do not manufacture a migration mapping or mutate production storage merely to exercise the migration path.** When historical records exist, their exact shape must first be profiled and mapped to the canonical domain contracts.

## Migration rules

1. Preserve the source unchanged.
2. Validate and report every source record.
3. Define a source-specific mapping to a canonical domain object.
4. Require all mandatory ownership, identity, jurisdiction, and provenance fields.
5. Refuse ambiguous records rather than guessing.
6. Persist only through the canonical provider-neutral repository contract.
7. Make migration idempotent using stable source identity where the canonical domain supports it.
8. Record migration evidence sufficient for audit and recovery.
9. Verify the destination before any future source retirement.
10. Never delete historical source data as part of migration execution.

## What this does not do

This boundary does not yet perform automatic complaint-to-`CivicCase` or rating-to-`AccountabilityFeedback` conversion. That work requires real historical records and an explicit schema mapping. The existing canonical contracts remain authoritative.

## Next storage phase

When durable production storage is ready, implement provider adapters against the existing repository contracts. The migration path should then be exercised against a disposable/test PostgreSQL environment before any production cutover, consistent with the existing PostgreSQL provider contract documentation.
