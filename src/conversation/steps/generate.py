from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import COMPLETED

from documents.complaint_builder import build_complaint

from docx import Document
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from services.id_generator import generate_complaint_id
from services.storage_service import save_complaint


# --------------------------------------------------
# 📄 DOCX GENERATOR
# --------------------------------------------------

def generate_docx(file_path: str, text: str):
    doc = Document()
    doc.add_heading("Complaint", 0)

    for line in text.split("\n"):
        doc.add_paragraph(line)

    doc.save(file_path)


# --------------------------------------------------
# 📄 PDF GENERATOR
# --------------------------------------------------

def generate_pdf(file_path: str, text: str):
    doc = SimpleDocTemplate(file_path)
    styles = getSampleStyleSheet()

    content = []

    for line in text.split("\n"):
        content.append(Paragraph(line, styles["Normal"]))
        content.append(Spacer(1, 10))

    doc.build(content)


# --------------------------------------------------
# 🚀 MAIN HANDLER
# --------------------------------------------------

async def handle_generate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # Safe message handling
    if update.callback_query:
        user_id = update.callback_query.from_user.id
        message = update.callback_query.message
    else:
        user_id = update.effective_user.id
        message = update.message

    session = get_session(user_id)

    # 🔥 Generate ID SAFELY HERE (correct place)
    if "complaint_id" not in session:
        session["complaint_id"] = generate_complaint_id()

    format_type = session.get("format", "pdf")

    await message.reply_text("📄 Generating your complaint document...")

    try:
        # --------------------------------------------------
        # 🧠 BUILD COMPLAINT
        # --------------------------------------------------

        complaint_text = build_complaint(
            issue=session.get("issue", ""),
            district=session.get("district", ""),
            department=session.get("department", ""),
            office_name=session.get("office", {}).get("office_name", ""),
            citizen_name="Concerned Citizen",
            category=session.get("category", "General"),
            complaint_id=session.get("complaint_id"),
        )

        # --------------------------------------------------
        # 📂 FILE GENERATION
        # --------------------------------------------------

        if format_type == "docx":
            file_path = f"/tmp/complaint_{user_id}.docx"
            filename = "complaint.docx"

            generate_docx(file_path, complaint_text)

        else:
            file_path = f"/tmp/complaint_{user_id}.pdf"
            filename = "complaint.pdf"

            generate_pdf(file_path, complaint_text)

        # --------------------------------------------------
        # 📤 SEND FILE
        # --------------------------------------------------

        with open(file_path, "rb") as file:
            await message.reply_document(
                document=file,
                filename=filename
            )

        await message.reply_text("✅ Complaint generated successfully.")

        # Save record
        save_complaint(session)

        # Complete state
        set_state(user_id, COMPLETED)

    except Exception as e:
        print("ERROR in handle_generate:", e)

        await message.reply_text(
            "❌ Failed to generate document. Please try again."
        )