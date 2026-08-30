"""Channel-neutral registry for authoritative civic procedure triggers.

No deadlines or legal conclusions are hard-coded here. Records must carry
provenance and be explicitly verified before they can drive case transitions.
"""

from __future__ import annotations

from datetime import date
from src.core.contracts.procedure_trigger import ProcedureTrigger, VerificationStatus


class SharedProcedureTriggerRegistry:
    def __init__(self, records: tuple[ProcedureTrigger, ...] = ()):
        self._records: dict[str, ProcedureTrigger] = {r.trigger_id: r for r in records}

    def register(self, record: ProcedureTrigger) -> None:
        if not record.source_id or not record.source_title or not record.source_url:
            raise ValueError("authoritative provenance is required")
        self._records[record.trigger_id] = record

    def get_verified(self, *, action: str, jurisdiction: str, on: date | None = None) -> tuple[ProcedureTrigger, ...]:
        effective_date = on or date.today()
        return tuple(
            record for record in self._records.values()
            if record.action == action
            and record.jurisdiction == jurisdiction
            and record.is_current(effective_date)
        )

    def verify(self, trigger_id: str) -> ProcedureTrigger:
        record = self._records[trigger_id]
        verified = ProcedureTrigger(
            trigger_id=record.trigger_id,
            action=record.action,
            jurisdiction=record.jurisdiction,
            condition=record.condition,
            trigger=record.trigger,
            source_id=record.source_id,
            source_title=record.source_title,
            source_url=record.source_url,
            effective_from=record.effective_from,
            effective_to=record.effective_to,
            verification=VerificationStatus.VERIFIED,
            notes=record.notes,
        )
        self._records[trigger_id] = verified
        return verified

    def mark_stale(self, trigger_id: str) -> ProcedureTrigger:
        record = self._records[trigger_id]
        stale = ProcedureTrigger(
            trigger_id=record.trigger_id,
            action=record.action,
            jurisdiction=record.jurisdiction,
            condition=record.condition,
            trigger=record.trigger,
            source_id=record.source_id,
            source_title=record.source_title,
            source_url=record.source_url,
            effective_from=record.effective_from,
            effective_to=record.effective_to,
            verification=VerificationStatus.STALE,
            notes=record.notes,
        )
        self._records[trigger_id] = stale
        return stale
