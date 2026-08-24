"""Atomic Supabase transition adapter for civic case state + audit event."""

from __future__ import annotations

from typing import Any

from src.core.civic_case import CaseEvent


class SupabaseCivicCaseTransaction:
    def __init__(self, client: Any) -> None:
        self.client = client

    def commit_transition(self, case_id: str, *, access_policy_ref: str, status: str, event: CaseEvent) -> CaseEvent:
        if not access_policy_ref.strip():
            raise PermissionError("An access policy reference is required")

        result = self.client.rpc(
            "append_civic_case_event",
            {
                "p_case_id": case_id,
                "p_access_policy_ref": access_policy_ref,
                "p_status": status,
                "p_event_id": event.event_id,
                "p_event_type": event.event_type.value,
                "p_occurred_at": event.occurred_at,
                "p_actor_ref": event.actor_id,
                "p_source_channel": event.source_channel,
                "p_notes": event.notes,
            },
        ).execute()
        return event
