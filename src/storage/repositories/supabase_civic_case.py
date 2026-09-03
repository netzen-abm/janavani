"""Supabase/PostgreSQL provider for the canonical CivicCase repository.

The adapter contains persistence mechanics only. Lifecycle validation,
authorization and consent decisions remain outside this provider.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.core.civic_case import (
    CaseEvent,
    CaseEventType,
    CaseStatus,
    CaseType,
    CivicCase,
)


class CivicCasePersistenceError(RuntimeError):
    """Raised when durable Civic Case persistence cannot be completed."""


class CivicCaseConcurrencyError(CivicCasePersistenceError):
    """Raised when a case changed between read and conditional update."""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _rows(response: Any) -> list[dict[str, Any]]:
    data = getattr(response, "data", None)
    if data is None:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        return [data]
    raise CivicCasePersistenceError("Unexpected Supabase response data")


def _case_row(case: CivicCase, *, created_at: str, updated_at: str,
              version: int) -> dict[str, Any]:
    return {
        "case_id": case.case_id,
        "case_type": case.case_type.value,
        "subject": case.subject,
        "narrative": case.narrative,
        "created_by": case.created_by,
        "jurisdiction_json": case.jurisdiction,
        "related_organisation_id": case.related_organisation_id,
        "related_office_id": case.related_office_id,
        "related_official_id": case.related_official_id,
        "related_representative_id": case.related_representative_id,
        "subject_claims_json": case.claims,
        "status": case.status.value,
        "created_at": created_at,
        "updated_at": updated_at,
        "version": version,
    }


def _event_row(event: CaseEvent) -> dict[str, Any]:
    return {
        "event_id": event.event_id,
        "case_id": event.case_id,
        "event_type": event.event_type.value,
        "occurred_at": event.occurred_at,
        "actor_id": event.actor_id,
        "source_channel": event.source_channel,
        "source_ref": event.source_ref,
        "notes": event.notes,
        "event_version": 1,
        "created_at": _now(),
    }


def _hydrate(row: dict[str, Any], events: list[dict[str, Any]],
             evidence: list[dict[str, Any]],
             documents: list[dict[str, Any]],
             consents: list[dict[str, Any]]) -> CivicCase:
    return CivicCase(
        case_id=str(row["case_id"]),
        case_type=CaseType(row["case_type"]),
        subject=str(row["subject"]),
        narrative=str(row["narrative"]),
        created_by=row.get("created_by"),
        jurisdiction=row.get("jurisdiction_json") or {},
        related_organisation_id=row.get("related_organisation_id"),
        related_office_id=row.get("related_office_id"),
        related_official_id=row.get("related_official_id"),
        related_representative_id=row.get("related_representative_id"),
        claims=row.get("subject_claims_json") or [],
        evidence_refs=[str(item["evidence_id"]) for item in evidence],
        document_refs=[str(item["document_id"]) for item in documents],
        consent_refs=[str(item["consent_id"]) for item in consents],
        status=CaseStatus(row["status"]),
        events=[
            CaseEvent(
                event_id=str(item["event_id"]),
                case_id=str(item["case_id"]),
                event_type=CaseEventType(item["event_type"]),
                occurred_at=str(item["occurred_at"]),
                actor_id=item.get("actor_id"),
                source_channel=item.get("source_channel"),
                source_ref=item.get("source_ref"),
                notes=item.get("notes"),
            )
            for item in events
        ],
    )


class SupabaseCivicCaseRepository:
    """PostgreSQL/Supabase implementation of CivicCaseRepository.

    The client is injected so the repository can be tested without a live
    Supabase service and without coupling the domain model to the provider.
    """

    def __init__(self, client: Any) -> None:
        if client is None:
            raise ValueError("A configured Supabase client is required")
        self._client = client

    def get(self, case_id: str) -> CivicCase | None:
        case_rows = self._select("civic_cases", case_id=case_id)
        if not case_rows:
            return None
        events = self._select("civic_case_events", case_id=case_id)
        evidence = self._select("civic_case_evidence_refs", case_id=case_id)
        documents = self._select("civic_case_document_refs", case_id=case_id)
        consents = self._select("civic_case_consents", case_id=case_id)
        return _hydrate(
            case_rows[0], events, evidence, documents, consents,
        )

    def save(self, case: CivicCase) -> None:
        existing = self._select("civic_cases", case_id=case.case_id)
        if not existing:
            self._insert_case(case)
            current_version = 1
        else:
            current_version = int(existing[0]["version"])
            self._update_case(case, existing[0])

        self._persist_events(case, current_version)
        self._persist_refs(case)

    def _select(self, table: str, *, case_id: str) -> list[dict[str, Any]]:
        try:
            response = (
                self._client.table(table)
                .select("*")
                .eq("case_id", case_id)
                .execute()
            )
            return _rows(response)
        except Exception as exc:
            raise CivicCasePersistenceError(
                f"Failed to read {table}"
            ) from exc

    def _insert_case(self, case: CivicCase) -> None:
        now = _now()
        try:
            response = (
                self._client.table("civic_cases")
                .insert(_case_row(
                    case, created_at=now, updated_at=now, version=1,
                ))
                .execute()
            )
            if not _rows(response):
                raise CivicCasePersistenceError("Case insert returned no row")
        except CivicCasePersistenceError:
            raise
        except Exception as exc:
            raise CivicCasePersistenceError("Failed to insert case") from exc

    def _update_case(self, case: CivicCase, row: dict[str, Any]) -> None:
        version = int(row["version"])
        created_at = str(row.get("created_at") or _now())
        try:
            response = (
                self._client.table("civic_cases")
                .update(_case_row(
                    case,
                    created_at=created_at,
                    updated_at=_now(),
                    version=version + 1,
                ))
                .eq("case_id", case.case_id)
                .eq("version", version)
                .execute()
            )
            if not _rows(response):
                raise CivicCaseConcurrencyError(
                    f"Stale CivicCase version for {case.case_id}"
                )
        except CivicCaseConcurrencyError:
            raise
        except Exception as exc:
            raise CivicCasePersistenceError("Failed to update case") from exc

    def _persist_events(self, case: CivicCase, version: int) -> None:
        existing = self._select("civic_case_events", case_id=case.case_id)
        existing_ids = {str(item["event_id"]) for item in existing}
        pending = [
            _event_row(event)
            for event in case.events
            if event.event_id not in existing_ids
        ]
        if not pending:
            return
        try:
            self._client.table("civic_case_events").insert(pending).execute()
        except Exception as exc:
            raise CivicCasePersistenceError(
                f"Failed to persist events for {case.case_id}"
            ) from exc

    def _persist_refs(self, case: CivicCase) -> None:
        try:
            if case.evidence_refs:
                evidence = [
                    {
                        "case_id": case.case_id,
                        "evidence_id": evidence_id,
                        "relationship": "case_evidence",
                        "created_at": _now(),
                    }
                    for evidence_id in case.evidence_refs
                ]
                self._client.table("civic_case_evidence_refs").upsert(
                    evidence,
                    on_conflict="case_id,evidence_id,relationship",
                ).execute()
            if case.document_refs:
                documents = [
                    {
                        "case_id": case.case_id,
                        "document_id": document_id,
                        "relationship": "case_document",
                        "version": 1,
                        "created_at": _now(),
                    }
                    for document_id in case.document_refs
                ]
                self._client.table("civic_case_document_refs").upsert(
                    documents,
                    on_conflict="case_id,document_id,relationship",
                ).execute()
        except Exception as exc:
            raise CivicCasePersistenceError(
                f"Failed to persist references for {case.case_id}"
            ) from exc
