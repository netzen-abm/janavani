"""Compatibility facade for the canonical document capability.

New callers should use ``documents.document_engine.DocumentEngine`` directly.
This service remains a thin application-layer entry point so existing imports
do not need to change in the same migration step.
"""

from documents.document_engine import DocumentEngine


def generate_complaint_document(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
):
    """Generate a complaint artifact through the canonical document engine."""
    return DocumentEngine().generate(
        "complaint",
        format_type=format_type,
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
    )
