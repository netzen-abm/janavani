import io
from pathlib import Path

from src.documents.document_contract import DocumentDraft, DocumentFormat, DocumentParty
from src.documents.renderers import render_document


def _sample_draft() -> DocumentDraft:
    return DocumentDraft(
        document_id="test-document",
        document_type="test",
        case_id="test-case",
        date="2026-09-08",
        subject="Constitutional Violation Analysis",
        body="Line 1: Constitutional Violation Analysis\nLine 2: Section 4 Details",
        to=DocumentParty(name="Test Authority"),
    )


def _rendered_bytes(document_format: DocumentFormat, tmp_path: Path) -> bytes:
    path = render_document(_sample_draft(), document_format, tmp_path)
    return path.read_bytes()


def test_pdf_generation_output_stream(tmp_path: Path):
    """Canonical renderer produces a valid PDF artifact."""
    binary_data = _rendered_bytes(DocumentFormat.PDF, tmp_path)
    assert isinstance(binary_data, bytes)
    assert binary_data.startswith(b"%PDF")


def test_docx_generation_output_stream(tmp_path: Path):
    """Canonical renderer produces a valid DOCX artifact."""
    binary_data = _rendered_bytes(DocumentFormat.DOCX, tmp_path)
    assert isinstance(binary_data, bytes)
    assert binary_data.startswith(b"PK")


def test_rendered_artifacts_are_non_empty(tmp_path: Path):
    """Both canonical output formats contain binary artifact data."""
    pdf_data = _rendered_bytes(DocumentFormat.PDF, tmp_path)
    docx_data = _rendered_bytes(DocumentFormat.DOCX, tmp_path)
    assert len(pdf_data) > 100
    assert len(docx_data) > 100
