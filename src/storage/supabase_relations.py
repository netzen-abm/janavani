"""Explicit persistence helpers for canonical relationship/event tables.

These helpers keep relationship writes and append-only event writes visible at
the repository boundary. Transactionality is delegated to the database/client
boundary and is not simulated here.
"""

from __future__ import annotations

from typing import Any


class SupabaseRelationRepository:
    """Persist canonical Case relationship references through Supabase."""

    def __init__(self, client: Any) -> None:
        if client is None:
            raise ValueError("Supabase client is required")
        self.client = client

    def link_evidence(self, case_id: str, evidence_id: str) -> None:
        self._upsert("case_evidence_refs", {"case_id": case_id, "evidence_id": evidence_id})

    def link_authority(self, case_id: str, authority_id: str) -> None:
        self._upsert("case_authority_refs", {"case_id": case_id, "authority_id": authority_id})

    def link_consent(self, case_id: str, consent_id: str) -> None:
        self._upsert("case_consent_refs", {"case_id": case_id, "consent_id": consent_id})

    def link_document(self, case_id: str, document_id: str) -> None:
        self._upsert("case_document_refs", {"case_id": case_id, "document_id": document_id})

    def link_submission(self, case_id: str, submission_id: str) -> None:
        self._upsert("case_submission_refs", {"case_id": case_id, "submission_id": submission_id})

    def append_case_event(
        self,
        case_id: str,
        event_type: str,
        *,
        actor: str | None = None,
        event_data: dict[str, Any] | None = None,
    ) -> None:
        self.client.table("case_events").insert(
            {
                "case_id": case_id,
                "event_type": event_type,
                "actor": actor,
                "event_data": dict(event_data or {}),
            }
        ).execute()

    def append_delivery_event(
        self,
        submission_id: str,
        status: str,
        *,
        adapter_id: str | None = None,
        reference: str | None = None,
        reason: str | None = None,
    ) -> None:
        self.client.table("delivery_events").insert(
            {
                "submission_id": submission_id,
                "status": status,
                "adapter_id": adapter_id,
                "reference": reference,
                "reason": reason,
            }
        ).execute()

    def _upsert(self, table: str, payload: dict[str, str]) -> None:
        self.client.table(table).upsert(payload).execute()
