"""Persistence boundary for canonical case relationships and append-only events.

The service layer owns business rules. Durable relationship/event writes use
privileged, explicitly-granted database functions so each relationship plus
its audit event is committed atomically.
"""

from __future__ import annotations

from typing import Any


class CanonicalRelationshipRepository:
    """Persist case relationships and events through canonical atomic RPCs."""

    def __init__(self, client: Any) -> None:
        if client is None:
            raise ValueError("Supabase client is required")
        self.client = client

    def link_evidence(self, case_id: str, evidence_id: str, *, actor: str | None = None) -> None:
        self._rpc("link_case_evidence_atomic", {
            "p_case_id": case_id,
            "p_evidence_id": evidence_id,
            "p_actor": actor,
        })

    def link_authority(self, case_id: str, authority_id: str, *, actor: str | None = None) -> None:
        self._rpc("link_case_authority_atomic", {
            "p_case_id": case_id,
            "p_authority_id": authority_id,
            "p_actor": actor,
        })

    def link_consent(self, case_id: str, consent_id: str, *, actor: str | None = None) -> None:
        self._rpc("link_case_consent_atomic", {
            "p_case_id": case_id,
            "p_consent_id": consent_id,
            "p_actor": actor,
        })

    def link_document(self, case_id: str, document_id: str, *, actor: str | None = None) -> None:
        self._rpc("link_case_document_atomic", {
            "p_case_id": case_id,
            "p_document_id": document_id,
            "p_actor": actor,
        })

    def link_submission(self, case_id: str, submission_id: str, *, actor: str | None = None) -> None:
        self._rpc("link_case_submission_atomic", {
            "p_case_id": case_id,
            "p_submission_id": submission_id,
            "p_actor": actor,
        })

    def append_case_event(
        self,
        case_id: str,
        event_type: str,
        *,
        actor: str | None = None,
        event_data: dict[str, Any] | None = None,
    ) -> None:
        self._rpc("append_case_event_atomic", {
            "p_case_id": case_id,
            "p_event_type": event_type,
            "p_actor": actor,
            "p_event_data": event_data or {},
        })

    def append_delivery_event(
        self,
        submission_id: str,
        status: str,
        *,
        adapter_id: str | None = None,
        reference: str | None = None,
        reason: str | None = None,
    ) -> None:
        # Delivery events currently have no atomic companion RPC because they
        # are standalone append-only observations. Keep the direct insert
        # explicit until delivery-state transitions are composed transactionally.
        self.client.table("delivery_events").insert({
            "submission_id": submission_id,
            "status": status,
            "adapter_id": adapter_id,
            "reference": reference,
            "reason": reason,
        }).execute()

    def _rpc(self, function_name: str, params: dict[str, Any]) -> None:
        self.client.rpc(function_name, params).execute()
