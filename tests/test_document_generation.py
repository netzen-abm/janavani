from src.documents.document_contract import DocumentDraft, DocumentFormat, DocumentParty
from src.documents.renderers import render_document


def _canonical_draft() -> DocumentDraft:
    return DocumentDraft(
        document_id="test-document",
        document_type="test",
        case_id="test-case",
        date="2026-09-09",
        subject="Constitutional Violation Analysis",
        body="Line 1: Constitutional Violation Analysis\nLine 2: Section 4 Details",
        to=DocumentParty(name="User-selected authority"),
    )


def test_pdf_generation_output_artifact(tmp_path):
    """Verifies that the canonical renderer writes a valid PDF artifact."""
    path = render_document(_canonical_draft(), DocumentFormat.PDF, tmp_path)

    assert path.is_file()
    assert path.read_bytes().startswith(b"%PDF")


def test_docx_generation_output_artifact(tmp_path):
    """Verifies that the canonical renderer writes a valid DOCX artifact."""
    path = render_document(_canonical_draft(), DocumentFormat.DOCX, tmp_path)

    assert path.is_file()
    assert path.read_bytes().startswith(b"PK")
