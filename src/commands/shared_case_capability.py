"""Telegram adapter over the canonical shared surface composition."""
from __future__ import annotations

from src.core.civic_case import CaseType, CivicCase
from src.identity.context import IdentityContext
from src.capabilities.civic_case import CivicCaseCreateRequest
from src.capabilities.civic_case_impl import CivicCaseCapability
from src.storage.repositories.civic_case import CivicCaseRepository


def create_case_from_telegram(
    repository: CivicCaseRepository,
    *,
    identity: IdentityContext,
    subject: str,
    narrative: str,
    case_capability: CivicCaseCapability | None = None,
    case_type: CaseType = CaseType.COMPLAINT,
    related_office_id: str | None = None,
) -> CivicCase:
    """Create a Telegram-originated case through shared infrastructure."""
    # The Telegram application passes the canonical composed capability. The
    # repository remains a compatibility seam for isolated tests/legacy callers;
    # it is used only when no composed capability is supplied.
    capability = case_capability or CivicCaseCapability(repository)
    # Telegram citizen content is transport-transient. Create only a metadata
    # shell in Janavani persistence; never persist the raw narrative.
    return capability.create_shell(
        CivicCaseCreateRequest(
            case_type=case_type,
            subject=subject,
            narrative="",
            related_office_id=related_office_id,
        ),
        identity=identity,
        source_channel="telegram",
    ).case



def create_case_for_telegram_session(
    *, user_id: int, context, session: dict, related_office_id: str | None = None
) -> CivicCase:
    """Create one metadata-only Case after the Telegram workflow resolves its destination."""
    from conversation.session import get_ephemeral_issue
    from src.adapters.telegram.identity import identity_for_telegram_user

    if session.get("case_id"):
        existing = context.application.bot_data["civic_case_capability"].get_owned(
            str(session["case_id"]),
            identity=identity_for_telegram_user(
                user_id, links=context.application.bot_data.get("identity_link_repository")
            ),
        )
        if existing is None:
            raise LookupError("Case not found")
        return existing

    issue = get_ephemeral_issue(user_id)
    if not issue:
        raise ValueError("The transient issue expired; please restart the complaint flow")
    links = context.application.bot_data.get("identity_link_repository")
    identity = identity_for_telegram_user(user_id, links=links)
    case_type = CaseType.RTI if str(session.get("document", "")).upper() == "RTI" else CaseType.COMPLAINT
    case = create_case_from_telegram(
        context.application.bot_data["case_repository"],
        identity=identity,
        subject=str(session.get("category") or "Citizen civic issue"),
        narrative=issue,
        case_capability=context.application.bot_data["civic_case_capability"],
        case_type=case_type,
        related_office_id=related_office_id,
    )
    session["case_id"] = case.case_id
    return case
