"""Compatibility bridge from legacy complaint sessions to CivicCase."""
from __future__ import annotations

from datetime import datetime, timezone

from core.civic_case import CaseEvent, CaseEventType, CaseType, CivicCase
from services.storage_service import save_complaint
from storage.repositories import CivicCaseRepository, create_civic_case_repository


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def session_to_civic_case(session: dict) -> CivicCase:
    """Translate the current Telegram session without changing its semantics."""
    case_id = session.get("complaint_id")
    if not case_id:
        raise ValueError("complaint_id is required for CivicCase migration")

    issue = (session.get("issue") or "").strip()
    office = session.get("office") or {}
    now = _now()

    event = CaseEvent(
        event_id=f"{case_id}:created",
        case_id=case_id,
        event_type=CaseEventType.CREATED,
        occurred_at=now,
        actor_id=None,
        source_channel="telegram",
        source_ref=str(case_id),
    )

    return CivicCase(
        case_id=case_id,
        case_type=CaseType.COMPLAINT,
        subject=issue[:120] or "Citizen complaint",
        narrative=issue,
        created_by=None,
        jurisdiction={
            "district": session.get("district"),
            "department": session.get("department"),
        },
        related_office_id=str(office.get("id")) if office.get("id") else None,
        status="draft",
        events=[event],
        created_at=now,
        updated_at=now,
    )


def persist_generated_complaint(
    session: dict,
    *,
    repository: CivicCaseRepository | None = None,
) -> CivicCase:
    """Persist through the canonical boundary while preserving legacy history.

    This is intentionally a dual-write migration step. The JSONL writer remains
    available for historical compatibility until migration evidence authorizes
    its retirement.
    """
    case = session_to_civic_case(session)
    repository = repository or create_civic_case_repository()
    repository.save(case)

    # Preserve the existing record during the migration window.
    save_complaint(session)
    return case
