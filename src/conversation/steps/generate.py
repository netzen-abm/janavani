"""Generate user-owned civic document artifacts through shared capabilities."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED
from conversation.session import get_session
from conversation.state import set_state
from src.capabilities.civic_action_capability import CivicActionCapability
from src.core.evidence import EvidenceRepository
from src.documents.document_contract import DocumentFormat
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.storage.artifact_blob import ArtifactBlobStore
from src.storage.repositories.artifact_provider import create_document_artifact_repository
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.document_artifact import DocumentArtifactRepository


@dataclass(frozen=True)
class TelegramGenerationDependencies:
    """Composition-level dependencies for Telegram generation."""

    case_repository: CivicCaseRepository
    civic_action_capability: CivicActionCapability
    artifact_repository: DocumentArtifactRepository
    blob_store: ArtifactBlobStore


def create_telegram_generation_dependencies(
    *,
    case_repository: CivicCaseRepository,
    civic_action_capability: CivicActionCapability,
) -> TelegramGenerationDependencies:
    """Compose Telegram dependencies from the canonical shared capability."""
    return TelegramGenerationDependencies(
        case_repository=case_repository,
        civic_action_capability=civic_action_capability,
        artifact_repository=create_document_artifact_repository(),
        blob_store=_create_blob_store(),
    )


def _create_blob_store() -> ArtifactBlobStore:
    from storage.artifact_blob_factory import create_artifact_blob_store
    return create_artifact_blob_store()


def _identity(user_id: int) -> IdentityContext:
    """Map a Telegram session to an opaque capability principal."""
    return IdentityContext(
        principal=Principal(
            principal_id=f"tg-session-{user_id}",
            identity_mode=IdentityMode.ANONYMOUS,
            interface="telegram",
            authentication_method=AuthenticationMethod.NONE,
            session_id=str(user_id),
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}),
        )
    )


def _document_format(value: str) -> DocumentFormat:
    return DocumentFormat.DOCX if value.strip().lower() == "docx" else DocumentFormat.PDF


def build_canonical_complaint_artifact(
    session: dict,
    *,
    dependencies: TelegramGenerationDependencies,
    user_id: int,
):
    """Build a canonical artifact through Case → Evidence → Authority → Document."""
    case_id = str(session.get("case_id") or "")
    if not case_id:
        raise ValueError("No canonical case is associated with this Telegram session")

    artifact = dependencies.civic_action_capability.generate_reviewable_artifact(
        case_id,
        identity=_identity(user_id),
        document_format=_document_format(str(session.get("format", "pdf"))),
        output_dir=Path("/tmp") / "janavani-artifacts" / "rendered",
        document_id=str(session.get("document_id") or f"doc-{case_id.removeprefix('case-')}"),
    )
    return artifact


async def handle_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
    else:
        user_id = update.effective_user.id
        message = update.message

    session = get_session(user_id)
    dependencies = context.application.bot_data.get("telegram_generation_dependencies")
    if dependencies is None:
        raise RuntimeError("Telegram generation dependencies were not composed")

    try:
        await message.reply_text("Generating document for your review...")
        artifact = build_canonical_complaint_artifact(
            session,
            dependencies=dependencies,
            user_id=user_id,
        )
        with dependencies.blob_store.open(artifact.reference.storage_ref) as handle:
            await message.reply_document(
                document=handle,
                filename=Path(artifact.reference.storage_ref).name,
            )
        dependencies.artifact_repository.save(artifact.reference.mark_downloaded())
        set_state(user_id, COMPLETED)
        await message.reply_text(
            "✅ Document generated and provided for your review, printing, or download.\n\n"
            "JanaVani has not submitted, emailed, or otherwise transmitted the document to the government."
        )
    except Exception as exc:
        print("ERROR in handle_generate:", exc)
        await message.reply_text("❌ Failed to generate document.")
