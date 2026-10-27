"""Regression tests for interactive Web MVP document templates."""
from io import BytesIO

import pytest
from docx import Document

from src.web_mvp.main import build_objection_document


def test_build_objection_document_pdf_is_a_pdf():
    """The PDF option returns bytes with a PDF media type and safe filename."""
    payload, media_type, filename = build_objection_document(
        "BILL-2026-KL-04", "Please publish the official bill text.", "pdf"
    )
    assert payload.startswith(b"%PDF-")
    assert media_type == "application/pdf"
    assert filename == "citizen_review_draft_BILL-2026-KL-04.pdf"


def test_build_objection_document_docx_preserves_user_observations():
    """The DOCX option keeps citizen-provided comments in an editable document."""
    payload, media_type, filename = build_objection_document(
        "BILL-2026-KL-04", "Please provide the source record.", "DOCX"
    )
    document = Document(BytesIO(payload))
    text = "\n".join(paragraph.text for paragraph in document.paragraphs)
    assert "Please provide the source record." in text
    assert "not legal advice" in text
    assert media_type.startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert filename.endswith(".docx")


def test_build_objection_document_rejects_unsafe_reference_and_format():
    """File references and formats are validated before filename construction."""
    with pytest.raises(ValueError):
        build_objection_document("../private/file", "comment", "PDF")
    with pytest.raises(ValueError):
        build_objection_document("BILL-1", "comment", "HTML")
