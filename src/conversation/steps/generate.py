"""Generate user-owned civic document artifacts through shared capabilities."""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from telegram import InputFile, Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED
from conversation.session import clear_ephemeral_issue, get_session
from conversation.state import set_state
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.capabilities.document_review import DocumentReviewCapability
from src.capabilities.letter_drafting import LetterDraftingCapability
from src.documents.document_contract import DocumentFormat
from src.documents.artifact_service import render_artifact_payload
from src.identity.context import IdentityContext
from src.identity.linking import ExternalIdentityLinkRepository
from src.adapters.telegram.identity import identity_for_telegram_user
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.document_artifact import DocumentArtifactRepository

import logging

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class TelegramGenerationDependencies:
    """Composition-level dependencies for Telegram generation."""

    case_repository: CivicCaseRepository
    case_capability: CivicCaseCapability
    civic_action_capability: CivicActionCapability
    consent_capability: ConsentCapability
    artifact_repository: DocumentArtifactRepository | None
    blob_store: ArtifactBlobStore | None
    identity_link_repository: ExternalIdentityLinkRepository | None = None
    letter_drafting_capability: LetterDraftingCapability | None = None
    document_review_capability: DocumentReviewCapability | None = None


def create_telegram_generation_dependencies(
    *,
    case_repository: CivicCaseRepository,
    case_capability: CivicCaseCapability,
    civic_action_capability: CivicActionCapability,
    consent_capability: ConsentCapability,
    artifact_repository: DocumentArtifactRepository | None = None,
    blob_store: ArtifactBlobStore | None = None,
    identity_link_repository: ExternalIdentityLinkRepository | None = None,
    letter_drafting_capability: LetterDraftingCapability | None = None,
    document_review_capability: DocumentReviewCapability | None = None,
) -> TelegramGenerationDependencies:
    """Compose Telegram dependencies from the canonical shared capabilities."""
    return TelegramGenerationDependencies(
        case_repository=case_repository,
        case_capability=case_capability,
        civic_action_capability=civic_action_capability,
        consent_capability=consent_capability,
        artifact_repository=artifact_repository,
        blob_store=blob_store,
        identity_link_repository=identity_link_repository or _MissingIdentityLinkRepository(),
        letter_drafting_capability=letter_drafting_capability,
        document_review_capability=document_review_capability,
    )


class _MissingIdentityLinkRepository:
    def find(self, provider: str, subject: str):
        return None

    def save(self, identity) -> None:
        raise PermissionError("Telegram identity linking is required")



def _identity(user_id: int, *, links: ExternalIdentityLinkRepository | None) -> IdentityContext:
    """Resolve a Telegram subject only after an explicit verified link."""
    if links is None:
        raise PermissionError("Telegram identity linking is required")
    return identity_for_telegram_user(user_id, links=links)

def _document_format(value: str) -> DocumentFormat:
    return DocumentFormat.DOCX if value.strip().lower() == "docx" else DocumentFormat.PDF


def build_canonical_complaint_artifact(
    session: dict,
    *,
    dependencies: TelegramGenerationDependencies,
    user_id: int,
):
    """Build an ephemeral artifact payload through shared capabilities."""
    case_id = str(session.get("case_id") or session.get("complaint_id") or "")
    if not case_id:
        raise ValueError("No canonical case is associated with this Telegram session")
    identity = _identity(user_id, links=dependencies.identity_link_repository)
    case = dependencies.case_capability.get_owned(case_id, identity=identity)
    if case is None:
        raise LookupError("Case not found")
    if getattr(case.status, "value", case.status) != "ready":
        raise PermissionError("Final Case readiness is required before Telegram document generation")
    if dependencies.document_review_capability is None:
        raise RuntimeError("Canonical document-review capability is unavailable")
    document_id = str(session.get("document_id") or "")
    if not document_id:
        raise LookupError("The reviewed document is unavailable")
    draft = dependencies.document_review_capability.get_owned(
        document_id, identity=identity
    )
    if draft is None or draft.case_id != case_id:
        raise LookupError("The reviewed document is unavailable")
    return render_artifact_payload(
        draft,
        _document_format(str(session.get("format", "pdf"))),
    )




async def handle_generate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the citizen an ephemeral reviewed document; never transmit it externally."""
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return
    session = get_session(user.id)
    dependencies = context.application.bot_data.get("telegram_generation_dependencies")
    if not isinstance(dependencies, TelegramGenerationDependencies):
        await message.reply_text("Document generation is temporarily unavailable.")
        return

    try:
        payload = build_canonical_complaint_artifact(
            session, dependencies=dependencies, user_id=user.id
        )
        await message.reply_document(
            document=InputFile(BytesIO(payload.content), filename=payload.filename),
            caption=(
                "Your Janavani document is ready for review. Save it locally and send it "
                "to the authority yourself. Janavani has not transmitted this document."
            ),
        )
        case_id = str(session.get("case_id") or "")
        identity = _identity(user.id, links=dependencies.identity_link_repository)
        if case_id:
            dependencies.case_capability.clear_transient_content(
                case_id, identity=identity
            )
        clear_ephemeral_issue(user.id)
        set_state(user.id, COMPLETED)
    except (LookupError, PermissionError, ValueError) as exc:
        logger.info(
            "telegram_document_generation_rejected error_type=%s",
            type(exc).__name__,
        )
        await message.reply_text(
            "I could not generate the document. Confirm that the Case has a verified "
            "authority and that your identity link is active, then restart the workflow."
        )
    except Exception as exc:
        logger.warning(
            "telegram_document_generation_failed error_type=%s",
            type(exc).__name__,
        )
        await message.reply_text(
            "Document generation is temporarily unavailable. Your Case has not been submitted."
        )
