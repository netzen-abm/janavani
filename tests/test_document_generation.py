import io

from datetime import date

from documents.document_contract import StructuredDocument
from documents.renderers import RendererRegistry


def sample_document() -> StructuredDocument:
    return StructuredDocument(
        document_type="complaint",
        document_id="JV-TEST-001",
        created_on=date(2026, 8, 25),
        content={
            "date": "2026-08-25",
            "user": {"name": "Test User", "address": "Test Address"},
            "office_id": "1",
            "issue": "Constitutional Violation Analysis",
        },
    )


def test_pdf_renderer_output_artifact():
    artifact = RendererRegistry().get("pdf").render(sample_document())
    assert artifact.format == "pdf"
    assert artifact.media_type == "application/pdf"
    assert isinstance(artifact.content, bytes)
    assert artifact.content.startswith(b"%PDF")


def test_docx_renderer_output_artifact():
    artifact = RendererRegistry().get("docx").render(sample_document())
    assert artifact.format == "docx"
    assert artifact.media_type.startswith("application/vnd.openxmlformats")
    assert isinstance(artifact.content, bytes)
    assert artifact.content.startswith(b"PK")
