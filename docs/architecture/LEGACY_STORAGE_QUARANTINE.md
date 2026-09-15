# Legacy Storage Quarantine

**Date:** 2026-09-15

## Decision

The legacy complaint/rating storage services are no longer runtime authorities.

Repository audit identified two unreferenced service-level persistence boundaries:

- `src/services/storage_service.py` — direct read/write of `database/complaints.jsonl`.
- `src/services/storage_adapter.py` — generic rating/complaint persistence using `database/ratings.jsonl` or an optional Supabase `ratings` table.

The historical implementations are preserved under `archive/legacy/storage/` and the active service paths have been removed/retired.

## Evidence

- `save_complaint` and `get_complaint_by_id` were defined only by the legacy storage service; repository search found no active caller.
- `save_rating_entry` was defined only by the legacy storage adapter; repository search found no active caller.
- Canonical accountability feedback now uses `AccountabilityFeedbackCapability` and an explicit repository boundary rather than a generic storage service.
- Canonical Case state belongs to the Case domain/repository boundaries rather than the legacy complaint JSONL service.

## Data preservation

`database/complaints.jsonl` and `database/ratings.jsonl` are **not deleted**. They remain historical/migration sources until formal data cutover is demonstrated.

## Architecture boundary

```text
Access Surface
    ↓
Canonical Capability
    ↓
Domain Repository Contract
    ↓
Provider Adapter
```

Legacy storage services must not be reintroduced as hidden alternate persistence authorities.

## Future migration

The next storage work should establish explicit migration/recovery tooling and canonical provider-neutral repository implementations. It should not introduce another generic `storage_adapter` abstraction.

Deletion of archived code or historical data requires evidence of successful migration, recovery/export validation, no remaining runtime dependency, and explicit retirement approval.
