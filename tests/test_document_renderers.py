"""Contract tests for shared PDF/DOCX renderers."""

from datetime import date

from src.documents.document_contract import StructuredDocument
from src.documents.docx_renderer import DocxRenderer
from src.documents.pdf_renderer import PdfRenderer


def sample_document() -> StructuredDocument:
    return StructuredDocument(
        document_type="complaint",
        document_id="CMP-TEST-001",
        created_on=date(2026, 8, 26),
        content={
            "issue": "Streetlight failure",
            "office_id": "office-1",
            "user": {"name": "Anonymous", "address": "Not Provided"},
        },
    )


def test_pdf_renderer_returns_artifact():
    artifact = PdfRenderer().render(sample_document())

    assert artifact.document_id == "CMP-TEST-001"
    assert artifact.format == "pdf"
    assert artifact.media_type == "application/pdf"
    assert artifact.content.startswith(b"%PDF")


def test_docx_renderer_returns_artifact():
    artifact = DocxRenderer().render(sample_document())

    assert artifact.document_id == "CMP-TEST-001"
    assert artifact.format == "docx"
    assert artifact.media_type.startswith("application/vnd.openxmlformats")
    assert artifact.content[:2] == b"PK"
