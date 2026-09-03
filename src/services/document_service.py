"""Compatibility service for canonical document generation.

New consumers should use the shared document capability directly. This module
preserves the legacy function signature while routing composition and
rendering through canonical contracts.

It never emails, submits, or otherwise transmits a generated document.
"""
from __future__ import annotations

from pathlib import Path

from src.documents.artifact_service import DocumentArtifact, generate_artifact
from src.documents.complaint_builder import build_complaint
from src.documents.document_contract import DocumentFormat
from src.documents.legacy_complaint_adapter import complaint_to_document_draft
from src.storage.repositories.authority_csv import CsvAuthorityRepository


_ARTIFACT_OUTPUT_DIR = Path("/tmp/janavani-artifacts/rendered")


def generate_complaint_document(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
) -> str:
    """Generate a printable/downloadable complaint artifact.

    The return value preserves the legacy path-oriented API. New consumers
    should use ``generate_complaint_artifact`` for structured metadata.
    """
    artifact = generate_complaint_artifact(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
        format_type=format_type,
    )
    return artifact.path


def generate_complaint_artifact(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
) -> DocumentArtifact:
    """Build a canonical complaint draft and render its artifact."""
    try:
        document_format = DocumentFormat(format_type.strip().lower())
    except ValueError as exc:
        raise ValueError(
            f"Unsupported document format: {format_type}. "
            f"Supported formats: {[item.value for item in DocumentFormat]}"
        ) from exc

    complaint = build_complaint(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
    )
    document_id = str(complaint["complaint_id"])
    draft = complaint_to_document_draft(
        complaint,
        document_id=document_id,
        case_id=document_id,
        authority_repository=CsvAuthorityRepository(),
    )
    return generate_artifact(
        draft,
        document_format,
        _ARTIFACT_OUTPUT_DIR,
    )
