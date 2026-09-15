# Legacy Storage Archive

Archived on 2026-09-15 as part of storage-boundary convergence.

## Retained artifacts

- `storage_service.py` — historical complaint JSONL persistence/lookup service.
- `storage_adapter.py` — historical generic ratings/complaint JSONL/Supabase adapter.

## Reason for quarantine

Repository audit found no active imports/callers for these legacy service boundaries. Their persistence model is inconsistent with the canonical Case and capability/repository architecture: `storage_service.py` treats complaint records as a standalone JSONL lifecycle, while `storage_adapter.py` is a generic rating/complaint writer rather than a domain-specific repository.

The historical implementations are preserved for recovery and migration analysis. They are not runtime authorities.

## Current authority

- Civic Case lifecycle and canonical Case repositories own case persistence and state.
- Accountability feedback uses `AccountabilityFeedbackCapability` → `AccountabilityFeedbackRepository` → provider adapter.
- Historical `database/ratings.jsonl` and `database/complaints.jsonl` remain preservation/migration sources until formal data cutover.

## Retirement rule

Do not delete archived artifacts or legacy data merely because they are unused. Deletion requires evidence of successful migration, recovery/export validation, no remaining runtime/documentation dependency, and explicit retirement approval.
