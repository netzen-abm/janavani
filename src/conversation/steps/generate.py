"""Generate user-owned civic document artifacts through shared capabilities."""
from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from telegram import Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED
from conversation.session import get_session
from conversation.state import set_state
from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability
from src.capabilities.consent import ConsentCapability
from src.documents.document_contract import DocumentFormat
from src.documents.artifact_service import render_artifact_payload
from src.identity.context import IdentityContext
from src.identity.linking import ExternalIdentityLinkRepository
from src.adapters.telegram.identity import identity_for_telegram_user
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.civic_case import CivicCaseRepository


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


def create_telegram_generation_dependencies(
    *,
    case_repository: CivicCaseRepository,
    case_capability: CivicCaseCapability,
    civic_action_capability: CivicActionCapability,
    consent_capability: ConsentCapability,
    artifact_repository: DocumentArtifactRepository | None = None,
    blob_store: ArtifactBlobStore | None = None,
    identity_link_repository: ExternalIdentityLinkRepository | None = None,
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
    draft = dependencies.civic_action_capability.build_document(
        case_id,
        identity=_identity(user_id, links=dependencies.identity_link_repository),
        document_id=str(session.get("document_id") or f"doc-{case_id.removeprefix('case-')}"),
    ).draft
    return render_artifact_payload(
        draft,
        _document_format(str(session.get("format", "pdf"))),
    )

