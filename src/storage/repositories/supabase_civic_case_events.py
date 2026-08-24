"""Supabase adapter for civic case audit events."""

from __future__ import annotations

from typing import Any

from src.core.civic_case import CaseEvent, CaseEventType
from src.storage.repositories.civic_case_events import CivicCaseEventRepository


class SupabaseCivicCaseEventRepository(CivicCaseEventRepository):
    def __init__(self, client: Any) -> None:
        self.client = client

    def append(self, event: CaseEvent, *, access_policy_ref: str) -> CaseEvent:
        self._require_policy(access_policy_ref)
        result = (
            self.client.table("civic_case_events")
            .insert({
                "event_id": event.event_id,
                "case_id": event.case_id,
                "event_type": event.event_type.value,
                "occurred_at": event.occurred_at,
                "actor_ref": event.actor_id,
                "source_channel": event.source_channel,
                "notes": event.notes,
            })
            .execute()
        )
        if not result.data:
            raise RuntimeError("Supabase did not return the civic audit event")
        return event

    def list_for_case(self, case_id: str, *, access_policy_ref: str) -> list[CaseEvent]:
        self._require_policy(access_policy_ref)
        result = (
            self.client.table("civic_case_events")
            .select("*")
            .eq("case_id", case_id)
            .order("occurred_at")
            .execute()
        )
        return [
            CaseEvent(
                event_id=row["event_id"],
                case_id=row["case_id"],
                event_type=CaseEventType(row["event_type"]),
                occurred_at=row["occurred_at"],
                actor_id=row.get("actor_ref"),
                source_channel=row.get("source_channel"),
                notes=row.get("notes"),
            )
            for row in (result.data or [])
        ]

    @staticmethod
    def _require_policy(policy: str) -> None:
        if not policy.strip():
            raise PermissionError("An access policy reference is required")
