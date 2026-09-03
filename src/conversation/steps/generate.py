"""Generate user-owned complaint artifacts through canonical capabilities."""
from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED
from conversation.session import get_session
from conversation.state import set_state

from documents.complaint_builder import build_complaint
from documents.artifact_ref import ArtifactState, DocumentArtifactRef
from documents.artifact_service import generate_artifact
from documents.document_contract import DocumentFormat
from documents.legacy_complaint_adapter import complaint_to_document_draft
from services.authority_service import find_authority
from services.case_migration import get_case_repository, persist_generated_complaint
from storage.repositories.document_artifact import (
    InMemoryDocumentArtifactRepository,
)


_ARTIFACT_REPOSITORY = InMemoryDocumentArtifactRepository()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _document_format(value: str) -> DocumentFormat:
    normalized = value.strip().lower()
    if normalized == DocumentFormat.DOCX.value:
        return DocumentFormat.DOCX
    return DocumentFormat.PDF


def build_canonical_complaint_artifact(session: dict):
    """Build a canonical draft and user-owned artifact from a legacy session."""
    complaint_id = str(session["complaint_id"])
    case = persist_generated_complaint(session)
    repository = get_case_repository()
    case = repository.get(case.case_id) or case

    office_id = str(case.related_office_id or "")
    authority = find_authority(office_id)
    if authority is None:
        raise ValueError("Selected office cannot be resolved")

    complaint = build_complaint(
        user_name=str(session.get("name") or session.get("citizen_name") or "Not Provided"),
        user_address=str(session.get("address") or "Not Provided"),
        office_id=office_id,
        issue_text=str(session.get("issue") or ""),
    )
    complaint["complaint_id"] = complaint_id

    draft = complaint_to_document_draft(
        complaint,
        document_id=complaint_id,
        case_id=case.case_id,
        authority_repository=type(
            "SingleAuthorityRepository",
            (),
            {
                "get": lambda _self, authority_id: (
                    authority if authority.authority_id == authority_id else None
                ),
            },
        )(),
    )

    document_format = _document_format(str(session.get("format", "pdf")))
    artifact = generate_artifact(
        draft,
        document_format,
        Path("/tmp") / "janavani-artifacts",
    )
    path = Path(artifact.path)
    artifact_id = f"{draft.document_id}:{document_format.value}"
    artifact_ref = DocumentArtifactRef(
        artifact_id=artifact_id,
        document_id=draft.document_id,
        case_id=draft.case_id,
        format=document_format.value,
        storage_ref=str(path),
        content_sha256=_sha256(path),
        state=ArtifactState.GENERATED,
    )
    _ARTIFACT_REPOSITORY.save(artifact_ref)

    case = repository.get(case.case_id) or case
    if artifact_id not in case.document_refs:
        case.add_document(
            artifact_id,
            event_id=f"{case.case_id}:document:{document_format.value}",
            occurred_at=date.today().isoformat(),
            source_channel="telegram",
        )
        repository.save(case)

    return path, artifact_ref


async def handle_generate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
    else:
        user_id = update.effective_user.id
        message = update.message

    session = get_session(user_id)
    if "complaint_id" not in session:
        from services.id_generator import generate_complaint_id

        session["complaint_id"] = generate_complaint_id()

    try:
        await message.reply_text("Generating document for your review...")
        file_path, artifact_ref = build_canonical_complaint_artifact(session)
        filename = file_path.name

        with file_path.open("rb") as handle:
            await message.reply_document(document=handle, filename=filename)

        downloaded = artifact_ref.mark_downloaded()
        _ARTIFACT_REPOSITORY.save(downloaded)
        set_state(user_id, COMPLETED)

        await message.reply_text(
            "✅ Document generated and provided for your review, "
            "printing, or download.\n\n"
            "JanaVani has not submitted, emailed, or otherwise transmitted "
            "the document to the government."
        )
    except Exception as exc:
        print("ERROR in handle_generate:", exc)
        await message.reply_text("❌ Failed to generate document.")
