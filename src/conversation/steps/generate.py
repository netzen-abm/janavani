"""Generate user-owned complaint artifacts through canonical capabilities."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from telegram import Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED
from conversation.session import get_session
from conversation.state import set_state

from documents.artifact_ref import ArtifactState
from documents.artifact_service import generate_artifact
from documents.document_contract import DocumentFormat
from documents.legacy_complaint_adapter import complaint_to_document_draft
from documents.complaint_builder import build_complaint
from services.authority_service import find_authority
from services.case_migration import get_case_repository, persist_generated_complaint
from storage.artifact_blob_factory import create_artifact_blob_store
from storage.repositories.artifact_provider import create_document_artifact_repository


def _document_format(value: str) -> DocumentFormat:
    return DocumentFormat.DOCX if value.strip().lower() == "docx" else DocumentFormat.PDF


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
        user_name=str(
            session.get("name")
            or session.get("citizen_name")
            or "Not Provided"
        ),
        user_address=str(session.get("address") or "Not Provided"),
        office_id=office_id,
        issue_text=str(session.get("issue") or ""),
    )
    complaint["complaint_id"] = complaint_id

    class SingleAuthorityRepository:
        def get(self, authority_id: str):
            return authority if authority.authority_id == authority_id else None

    draft = complaint_to_document_draft(
        complaint,
        document_id=complaint_id,
        case_id=case.case_id,
        authority_repository=SingleAuthorityRepository(),
    )

    document_format = _document_format(str(session.get("format", "pdf")))
    output_dir = Path("/tmp") / "janavani-artifacts" / "rendered"
    artifact = generate_artifact(
        draft,
        document_format,
        output_dir,
        blob_store=create_artifact_blob_store(),
    )
    artifact_repository = create_document_artifact_repository()
    artifact_repository.save(artifact.reference)

    case = repository.get(case.case_id) or case
    artifact_id = artifact.reference.artifact_id
    if artifact_id not in case.document_refs:
        case.add_document(
            artifact_id,
            event_id=f"{case.case_id}:document:{document_format.value}",
            occurred_at=datetime.now(timezone.utc).isoformat(),
            source_channel="telegram",
        )
        repository.save(case)

    return artifact


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
        artifact = build_canonical_complaint_artifact(session)

        with open(artifact.path, "rb") as handle:
            await message.reply_document(
                document=handle,
                filename=Path(artifact.path).name,
            )

        artifact_repository = create_document_artifact_repository()
        artifact_repository.save(artifact.reference.mark_downloaded())
        set_state(user_id, COMPLETED)
        await message.reply_text(
            "✅ Document generated and provided for your review, printing, "
            "or download.\n\n"
            "JanaVani has not submitted, emailed, or otherwise transmitted "
            "the document to the government."
        )
    except Exception as exc:
        print("ERROR in handle_generate:", exc)
        await message.reply_text("❌ Failed to generate document.")
