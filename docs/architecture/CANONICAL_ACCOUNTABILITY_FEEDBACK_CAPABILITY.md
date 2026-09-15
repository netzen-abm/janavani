# Canonical Accountability Feedback Capability

**Status:** IMPLEMENTATION — bounded migration

## Purpose

Accountability feedback is a shared Janavani capability for structured citizen experience of a public-service office. It is not a Telegram feature and it is not a complaint-storage shortcut.

## Boundary

```text
Access Surface
    ↓
AccountabilityFeedbackCapability
    ↓
AccountabilityFeedbackRepository
    ↓
Provider Adapter
```

The capability owns validation, sanitisation, canonical feedback identity and the feedback record contract. The repository owns persistence. Access surfaces must not write `database/ratings.jsonl` directly.

## Current migration

- Canonical domain contract: `src/core/accountability_feedback.py`
- Canonical capability: `src/capabilities/accountability_feedback.py`
- Development repository: `src/storage/repositories/accountability_feedback.py`
- Current persistence adapter: `src/storage/repositories/accountability_feedback_jsonl.py`
- Telegram adapter: `src/commands/rate.py`
- Historical implementation: `archive/legacy/feedback/rate_office.py`
- Active legacy entry point: `src/services/rate_office.py` is now fail-closed.

The JSONL adapter deliberately preserves the existing `database/ratings.jsonl` shape so existing data remains recoverable during migration. This is a persistence compatibility decision, not a declaration that JSONL is the final production provider.

## Security and privacy

- Ratings are constrained to 1–5.
- Commentary is sanitised before persistence.
- Existing content-safety validation is reused.
- Telegram actor identity is represented as a provider-neutral actor reference and the JSONL adapter stores only a short privacy hash.
- Feedback submission is a persistence operation; it does not imply external delivery, authority action, or resolution of a case.

## Non-goals

This capability does not:

- submit a complaint to a government authority;
- choose a delivery channel;
- transport an external message;
- assert that an allegation is verified;
- mutate a canonical civic case;
- own Telegram, Web, WhatsApp, Android, iOS or DApp business logic.

If feedback becomes linked to a case, that relationship must be explicit rather than inferred from a rating record.

## Archive-first rule

The historical rating service is retained under `archive/legacy/feedback/`. Deletion is deferred until migration evidence demonstrates that recovery, historical-data access and all required compatibility checks are satisfied.
