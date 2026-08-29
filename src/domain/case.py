"""Canonical civic case domain contract.

The case is the shared product object. Access surfaces must never own this
state; they submit channel-neutral commands through the case service.
"""
from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class CaseStatus(str, Enum):
    DRAFT = "draft"
    READY_FOR_REVIEW = "ready_for_review"
    APPROVED = "approved"
    SUBMITTED = "submitted"
    TRACKING = "tracking"


class CaseCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=10000)
    location: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=120)


class CaseUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=10, max_length=10000)
    location: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=120)


class CaseRecord(BaseModel):
    id: str
    title: str
    description: str
    location: str | None = None
    category: str | None = None
    status: CaseStatus = CaseStatus.DRAFT
    created_at: datetime
    updated_at: datetime
    evidence: list[dict[str, Any]] = Field(default_factory=list)
    timeline: list[dict[str, Any]] = Field(default_factory=list)

    @classmethod
    def new(cls, payload: CaseCreate) -> "CaseRecord":
        now = datetime.now(timezone.utc)
        case_id = f"JNV-{uuid4().hex[:12].upper()}"
        return cls(
            id=case_id,
            title=payload.title.strip(),
            description=payload.description.strip(),
            location=payload.location.strip() if payload.location else None,
            category=payload.category.strip() if payload.category else None,
            created_at=now,
            updated_at=now,
            timeline=[{"event": "case_created", "at": now.isoformat()}],
        )


class CaseRepository:
    """Provider-neutral repository contract used by the case capability."""

    def create(self, case: CaseRecord) -> CaseRecord:  # pragma: no cover - interface
        raise NotImplementedError

    def get(self, case_id: str) -> CaseRecord | None:  # pragma: no cover - interface
        raise NotImplementedError

    def list(self) -> list[CaseRecord]:  # pragma: no cover - interface
        raise NotImplementedError

    def update(self, case: CaseRecord) -> CaseRecord:  # pragma: no cover - interface
        raise NotImplementedError


class InMemoryCaseRepository(CaseRepository):
    """Development repository; replaceable by the production storage adapter."""

    def __init__(self) -> None:
        self._cases: dict[str, CaseRecord] = {}

    def create(self, case: CaseRecord) -> CaseRecord:
        self._cases[case.id] = case
        return case

    def get(self, case_id: str) -> CaseRecord | None:
        return self._cases.get(case_id)

    def list(self) -> list[CaseRecord]:
        return sorted(self._cases.values(), key=lambda item: item.updated_at, reverse=True)

    def update(self, case: CaseRecord) -> CaseRecord:
        self._cases[case.id] = case
        return case
