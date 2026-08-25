"""Compatibility facade for legacy complaint-PDF imports.

Canonical implementation: ``documents.document_engine.DocumentEngine``.
No business logic or independent rendering remains here.
"""

from documents.document_engine import DocumentEngine


def generate_pdf_from_complaint(complaint: dict):
    """Render an already-composed complaint payload as a PDF artifact."""
    from documents.renderers import DocumentRenderer
    return DocumentRenderer.render(complaint, "pdf")


def generate_complaint_pdf(user_name, user_address, office_id, issue_text):
    """Legacy function facade retained while callers migrate."""
    return DocumentEngine().generate(
        "complaint",
        format_type="pdf",
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
    )
