# Archived Legacy Escalation Path

Archived on 2026-09-15 after repository-wide search found no production caller for the legacy escalation runner beyond the runner's own internal reference chain.

## Retained artifacts

- `escalation_rules.py` — historical category-to-target rules.
- `escalation_engine.py` — historical JSONL-based overdue detection and mutation.
- `escalation_runner.py` — historical batch runner.

## Canonical replacement

The canonical escalation boundary is `src/capabilities/escalation.py`, exposed through `CivicActionVerticalSlice` and shared platform composition.

The canonical capability is decision-only. It does not persist, mutate, submit, or transport escalation. External action must continue through authorization, consent, approval, verified channel, submission, idempotency, delivery, and acknowledgement boundaries.

## Retirement evidence

The legacy implementation directly reads/writes `database/ratings.jsonl` and is not the source of truth for the canonical Case lifecycle. Repository search for `run_escalation_cycle`, `check_overdue_complaints`, and `src.services.escalation` found only the legacy implementation itself; no additional caller was found.

This archive is intentionally retained. Deletion requires a later evidence-based decision under the repository's archive-first rule.
