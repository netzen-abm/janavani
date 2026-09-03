"""Compatibility bridge from legacy complaint sessions to CivicCase."""
from __future__ import annotations

from datetime import datetime, timezone

from core.civic_case import (
    CaseEvent,
    CaseEventType,
    CaseStatus,
    CaseType,
    CivicCase,
)
from services.storage_service import save_complaint
from storage.repositories import CivicCaseRepository, create_civic_case_repository


_REPOSITORY: CivicCaseRepository | None = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def get_case_repository() -> CivicCaseRepository:
    """Reuse the selected repository for this process lifetime."""
    global _REPOSITORY
    if _REPOSITORY is None:
        _REPOSITORY = create_civic_case_repository()
    return _REPOSITORY


def session_to_civic_case(session: dict) -> CivicCase:
    """Translate a legacy Telegram session into a new CivicCase."""
    case_id = session.get("complaint_id")
    if not case_id:
        raise ValueError("complaint_id is required for CivicCase migration")

    issue = (session.get("issue") or "").strip()
    office = session.get("office") or {}
    office_id = office.get("office_id") or office.get("id")
    now = _now()

    event = CaseEvent(
        event_id=f"{case_id}:created",
        case_id=case_id,
        event_type=CaseEventType.CREATED,
        occurred_at=now,
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
        related_office_id=str(office_id) if office_id else None,
        status=CaseStatus.DRAFT,
        events=[event],
        created_at=now,
        updated_at=now,
    )


def persist_case(case: CivicCase, *, repository: CivicCaseRepository | None = None):
    (repository or get_case_repository()).save(case)
    return case


def persist_generated_complaint(
    session: dict,
    *,
    repository: CivicCaseRepository | None = None,
) -> CivicCase:
    """Persist without ever downgrading an already-reviewed/ready case."""
    repo = repository or get_case_repository()
    case_id = session.get("complaint_id")
    case = repo.get(case_id) if case_id else None
    if case is None:
        case = session_to_civic_case(session)
        repo.save(case)

    # Preserve the existing JSONL record during migration.
    save_complaint(session)
    return case


def record_submission_consent(
    session: dict,
    *,
    repository: CivicCaseRepository | None = None,
) -> CivicCase:
    """Record explicit consent and move the case to READY."""
    case_id = session.get("complaint_id")
    if not case_id:
        raise ValueError("complaint_id is required for consent")

    repo = repository or get_case_repository()
    case = repo.get(case_id)
    if case is None:
        case = session_to_civic_case(session)

    consent_id = f"telegram:{case_id}:submission"
    if consent_id not in case.consent_refs:
        case.consent_refs.append(consent_id)

    if case.status is CaseStatus.DRAFT:
        case.start_review(
            event_id=f"{case_id}:review",
            occurred_at=_now(),
            actor_id=f"telegram:{session.get('telegram_user_id', 'unknown')}",
        )

    if case.status is CaseStatus.REVIEW:
        case.mark_ready(
            event_id=f"{case_id}:approved",
            occurred_at=_now(),
            actor_id=f"telegram:{session.get('telegram_user_id', 'unknown')}",
        )
    elif case.status is not CaseStatus.READY:
        raise ValueError(
            f"Case cannot record new submission consent from {case.status.value}"
        )

    repo.save(case)
    return case
