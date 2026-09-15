# Legacy Complaint Tracking Quarantine

**Date:** 2026-09-15

## Decision

The historical `src/services/track_complaint.py` implementation is retired from active execution.

The implementation directly read and rewrote `database/ratings.jsonl`, maintained its own complaint status vocabulary, and therefore bypassed the canonical Case lifecycle and shared capability boundaries.

## Archive-first evidence

The historical implementation is preserved at:

- `archive/legacy/feedback/track_complaint.py`

The active path is retained only as a fail-closed compatibility tombstone. It performs no JSONL reads, writes, status mutation, transport, or external side effect.

## Canonical ownership

Case status and lifecycle belong to the canonical Case domain/capability boundaries. Follow-up recommendations belong to `FollowUpCapability` and remain user-controlled.

`database/ratings.jsonl` is preserved as a legacy data/recovery source. It is not deleted or treated as the canonical Case store.

## Evidence from repository audit

Repository search found the active definitions of `get_complaint_status`, `list_user_complaints`, and `update_complaint_status` only in the legacy tracker. No active import of `src.services.track_complaint` was found in the repository search performed for this quarantine.

## Retirement rule

The archived implementation and legacy data remain until a later evidence-based migration/deletion decision confirms that:

1. all required historical data has been migrated or explicitly preserved;
2. no supported surface depends on the legacy tracker;
3. canonical Case tracking covers the required user journeys;
4. rollback/recovery evidence is sufficient.

Until then, **Archive first. Delete only after evidence.**
