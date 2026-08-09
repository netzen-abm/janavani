# src/services/document_service.py

from documents.complaint_builder import build_complaint
from documents.generate_pdf import generate_pdf_from_complaint


def generate_complaint_document(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf"
) -> str:
    """
    Central document generation service
    """

    # 1. Build complaint
    complaint = build_complaint(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text
    )

    # 2. Format handling
    if format_type.lower() == "pdf":
        return generate_pdf_from_complaint(complaint)

    elif format_type.lower() == "docx":
        return "DOCX generation not implemented yet"

    else:
        return "Invalid format selected"
