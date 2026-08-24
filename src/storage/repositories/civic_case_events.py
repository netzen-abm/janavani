"""Audit-event persistence boundary for civic case lifecycle events."""

from __future__ import annotations

from typing import Protocol

from src.core.civic_case import CaseEvent


class CivicCaseEventRepository(Protocol):
    def append(self, event: CaseEvent, *, access_policy_ref: str) -> CaseEvent: ...
    def list_for_case(self, case_id: str, *, access_policy_ref: str) -> list[CaseEvent]: ...


class InMemoryCivicCaseEventRepository:
    def __init__(self) -> None:
        self._events: dict[str, CaseEvent] = {}

    def append(self, event: CaseEvent, *, access_policy_ref: str) -> CaseEvent:
        if not access_policy_ref.strip():
            raise PermissionError("An access policy reference is required")
        if event.event_id in self._events:
            raise ValueError("Event already exists")
        self._events[event.event_id] = event
        return event

    def list_for_case(self, case_id: str, *, access_policy_ref: str) -> list[CaseEvent]:
        if not access_policy_ref.strip():
            raise PermissionError("An access policy reference is required")
        return [event for event in self._events.values() if event.case_id == case_id]
