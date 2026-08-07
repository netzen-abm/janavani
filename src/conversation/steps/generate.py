"""
Generate Step

Generates the final document
from the completed conversation.
"""

from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.session import clear_session

from conversation.state import clear_state

from documents.document_engine import DocumentEngine
from documents.pdf_generator import PDFGenerator


async def handle_generate(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
):
    """
    Generate the final document.
    """

    user_id = update.effective_user.id

    session = get_session(user_id)

    await update.message.reply_text(
        "Generating your document..."
    )

    document_engine = DocumentEngine()

    pdf_generator = PDFGenerator()

    document_text = document_engine.generate(
        document_type=session["document"],
        issue=session["issue"],
        office_name=session["office"]["office_name"],
        office_address=session["office"]["office_address"],
        identity_mode=session.get("identity_mode", "anonymous"),
    )

    pdf_file = pdf_generator.generate(
        text=document_text,
        output_file=f"complaint_{user_id}.pdf",
    )

    with open(pdf_file, "rb") as pdf:

        await update.message.reply_document(
            document=pdf,
            filename=f"complaint_{user_id}.pdf",
            caption="✅ Your complaint has been generated successfully."
        )

    clear_session(user_id)
    clear_state(user_id)

try:
    ...
finally:
    ...