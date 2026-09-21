"""Compatibility bridge from legacy Telegram sessions to CivicCase.

The bridge remains temporarily because the conversation state machine is
still being migrated. The canonical CivicCase repository is authoritative;
legacy JSONL complaint persistence is no longer written by this bridge.
"""
from __future__ import annotations

from datetime import datetime, timezone

from core.civic_case import (
    CaseEvent,
    CaseEventType,
    CaseStatus,
    CaseType,
    CivicCase,
)
from storage.repositories import CivicCaseRepository


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _telegram_actor_id(session: dict) -> str:
    telegram_user_id = session.get("telegram_user_id")
    if telegram_user_id is None:
        raise ValueError("telegram_user_id is required for CivicCase ownership")
    return f"telegram:{telegram_user_id}"


def session_to_civic_case(session: dict) -> CivicCase:
    """Translate a legacy Telegram session into a new owned CivicCase."""
    case_id = session.get("complaint_id")
    if not case_id:
        raise ValueError("complaint_id is required for CivicCase migration")

    issue = (session.get("issue") or "").strip()
    office = session.get("office") or {}
    office_id = office.get("office_id") or office.get("id")
    now = _now()
    actor_id = _telegram_actor_id(session)

    event = CaseEvent(
        event_id=f"{case_id}:created",
        case_id=case_id,
        event_type=CaseEventType.CREATED,
        occurred_at=now,
        actor_id=actor_id,
        source_channel="telegram",
        source_ref=str(case_id),
    )

    return CivicCase(
        case_id=case_id,
        case_type=CaseType.COMPLAINT,
        subject=issue[:120] or "Citizen complaint",
        narrative=issue,
        created_by=actor_id,
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


def persist_case(case: CivicCase, *, repository: CivicCaseRepository):
    """Persist a case through the caller-owned repository boundary."""
    repository.save(case)
    return case


def persist_generated_complaint(
    session: dict,
    *,
    repository: CivicCaseRepository,
) -> CivicCase:
    """Persist a Telegram complaint in the canonical Case repository."""
    case_id = session.get("complaint_id")
    case = repository.get(case_id) if case_id else None
    if case is None:
        case = session_to_civic_case(session)
        repository.save(case)
    return case


def record_submission_consent(
    session: dict,
    *,
    repository: CivicCaseRepository,
) -> CivicCase:
    """Record explicit consent and move the owned case to READY."""
    case_id = session.get("complaint_id")
    if not case_id:
        raise ValueError("complaint_id is required for consent")

    case = repository.get(case_id)
    if case is None:
        case = session_to_civic_case(session)

    consent_id = f"telegram:{case_id}:submission"
    if consent_id not in case.consent_refs:
        case.consent_refs.append(consent_id)

    actor_id = _telegram_actor_id(session)

    if case.status is CaseStatus.DRAFT:
        case.start_review(
            event_id=f"{case_id}:review",
            occurred_at=_now(),
            actor_id=actor_id,
        )

    if case.status is CaseStatus.REVIEW:
        case.mark_ready(
            event_id=f"{case_id}:approved",
            occurred_at=_now(),
            actor_id=actor_id,
        )
    elif case.status is not CaseStatus.READY:
        raise ValueError(
            f"Case cannot record new submission consent from {case.status.value}"
        )

    repository.save(case)
    return case
