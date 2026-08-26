"""Telegram document-generation step using shared document capabilities."""

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes

from conversation.constants import COMPLETED
from conversation.session import get_session
from conversation.state import set_state
from src.capabilities.document_capability import DocumentCapability
from src.documents.docx_renderer import DocxRenderer
from src.documents.pdf_renderer import PdfRenderer
from src.documents.document_contract import DocumentRequest
from src.documents.complaint_builder import build_complaint
from services.storage_service import save_complaint


def _document_capability() -> DocumentCapability:
    """Compose the shared document capability at the interface boundary."""
    return DocumentCapability(
        builder=build_complaint,
        renderers={"pdf": PdfRenderer(), "docx": DocxRenderer()},
    )


async def handle_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Render the canonical complaint document and deliver its artifact."""
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
    else:
        user_id = update.effective_user.id
        message = update.message

    session = get_session(user_id)
    format_type = session.get("format", "pdf")

    try:
        office = session.get("office", {})
        request = DocumentRequest(
            document_type="complaint",
            user_name="Anonymous",
            user_address="Not Provided",
            office_id=str(office.get("id", "1")),
            issue_text=session.get("issue", ""),
            metadata={"channel": "telegram", "actor_id": str(user_id)},
        )

        capability = _document_capability()
        document = capability.build(request)
        artifact = capability.render(document, format_type)

        await message.reply_text(
            "📄 Final Complaint Text:\n\n"
            + str(document.content.get("issue", ""))
        )
        await message.reply_document(
            document=artifact.content,
            filename=artifact.filename,
        )
        await message.reply_text("✅ Complaint generated successfully.")

        session["complaint"] = document
        session["document_id"] = document.document_id
        save_complaint(session)
        set_state(user_id, COMPLETED)

    except Exception as exc:
        print("ERROR in handle_generate:", exc)
        await message.reply_text("❌ Failed to generate document.")
