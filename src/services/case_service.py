"""Canonical case capability service.

This service owns case lifecycle semantics; web, Telegram, mobile and DApp
surfaces must call this capability rather than implement their own case logic.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone

from src.domain.case import CaseCreate, CaseRecord, CaseStatus, CaseUpdate, InMemoryCaseRepository


class CaseService:
    def __init__(self, repository: InMemoryCaseRepository | None = None) -> None:
        self.repository = repository or InMemoryCaseRepository()

    def create_case(self, payload: CaseCreate) -> CaseRecord:
        return self.repository.create(CaseRecord.new(payload))

    def get_case(self, case_id: str) -> CaseRecord | None:
        case = self.repository.get(case_id)
        return deepcopy(case) if case else None

    def list_cases(self) -> list[CaseRecord]:
        return [deepcopy(case) for case in self.repository.list()]

    def update_case(self, case_id: str, payload: CaseUpdate) -> CaseRecord | None:
        case = self.repository.get(case_id)
        if case is None:
            return None
        changes = payload.model_dump(exclude_unset=True)
        for field, value in changes.items():
            if value is not None:
                setattr(case, field, value.strip() if isinstance(value, str) else value)
        case.updated_at = datetime.now(timezone.utc)
        case.timeline.append({"event": "case_updated", "at": case.updated_at.isoformat()})
        return self.repository.update(case)

    def transition(self, case_id: str, status: CaseStatus) -> CaseRecord | None:
        case = self.repository.get(case_id)
        if case is None:
            return None
        case.status = status
        case.updated_at = datetime.now(timezone.utc)
        case.timeline.append({"event": f"status:{status.value}", "at": case.updated_at.isoformat()})
        return self.repository.update(case)
