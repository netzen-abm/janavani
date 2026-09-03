"""Contract tests for user-controlled document artifact generation."""
from pathlib import Path

from src.documents.artifact_service import generate_artifact
from src.documents.document_contract import (
    DocumentDraft,
    DocumentFormat,
    DocumentParty,
)


def make_draft() -> DocumentDraft:
    return DocumentDraft(
        document_id="DOC-TEST-1",
        document_type="complaint",
        case_id="CASE-TEST-1",
        date="2026-09-03",
        subject="Test subject",
        body="Test body",
        to=DocumentParty(
            name="District Authority",
            address="Test address",
            email="authority@example.test",
            role="Public Authority",
        ),
        cc=(
            DocumentParty(
                name="Department Head",
                address="CC address",
                email="cc@example.test",
            ),
        ),
        sender=DocumentParty(name="Citizen", address="Citizen address"),
    )


def test_pdf_artifact_is_created(tmp_path: Path):
    artifact = generate_artifact(
        make_draft(), DocumentFormat.PDF, tmp_path
    )
    assert artifact.case_id == "CASE-TEST-1"
    assert artifact.format is DocumentFormat.PDF
    assert Path(artifact.path).is_file()
    assert Path(artifact.path).suffix == ".pdf"


def test_docx_artifact_is_created(tmp_path: Path):
    artifact = generate_artifact(
        make_draft(), DocumentFormat.DOCX, tmp_path
    )
    assert artifact.format is DocumentFormat.DOCX
    assert Path(artifact.path).is_file()
    assert Path(artifact.path).suffix == ".docx"
