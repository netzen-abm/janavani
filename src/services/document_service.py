"""Document capability service with shared authorization enforcement."""

from documents.complaint_builder import build_complaint
from documents.generate_pdf import generate_pdf_from_complaint

from src.authorization.endpoint import authorize_capability
from src.identity.context import IdentityContext


DOCUMENT_GENERATE_CAPABILITY = "citizen.document.generate"


def generate_complaint_document(
    context: IdentityContext,
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
) -> str:
    """Generate a complaint document only after shared authorization.

    The authorization boundary is deliberately evaluated before document
    generation. Authentication, consent, and external delivery remain
    separate concerns and are not implied by this function.
    """
    authorize_capability(context, DOCUMENT_GENERATE_CAPABILITY)

    complaint = build_complaint(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
    )

    selected_format = format_type.lower()
    if selected_format == "pdf":
        return generate_pdf_from_complaint(complaint)

    if selected_format == "docx":
        return "DOCX generation not implemented yet"

    return "Invalid format selected"
