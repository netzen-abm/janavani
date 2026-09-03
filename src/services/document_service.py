"""Compatibility service for canonical document generation.

New consumers should use the canonical document and artifact capabilities.
This adapter preserves the legacy function signature during migration.
It never emails, submits, or otherwise transmits a generated document.
"""
from __future__ import annotations

from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.document_contract import DocumentFormat
from src.documents.legacy_complaint_adapter import complaint_to_document_draft
from src.documents.complaint_builder import build_complaint
from src.storage.repositories.authority_csv import CsvAuthorityRepository


def generate_complaint_document(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
) -> str:
    """Generate a printable/downloadable complaint artifact and return its path."""
    return generate_complaint_artifact(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
        format_type=format_type,
    ).path


def generate_complaint_artifact(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
) -> DocumentArtifact:
    """Build a canonical complaint draft and render it through shared capability."""
    try:
        document_format = DocumentFormat(format_type.strip().lower())
    except ValueError as exc:
        raise ValueError(f"Unsupported document format: {format_type}") from exc

    complaint = build_complaint(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
    )
    draft = complaint_to_document_draft(
        complaint,
        document_id=str(complaint["complaint_id"]),
        case_id=str(complaint["complaint_id"]),
        authority_repository=CsvAuthorityRepository(),
    )
    return generate_artifact(
        draft,
        document_format,
        "/tmp/janavani-artifacts/rendered",
    )
