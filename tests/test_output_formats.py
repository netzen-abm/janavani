import pytest

from src.documents.output_formats import OutputFormat, resolve_output_format


def test_pdf_choice_resolves_to_pdf():
    spec = resolve_output_format("pdf")
    assert spec.format is OutputFormat.PDF
    assert spec.extension == ".pdf"
    assert spec.media_type == "application/pdf"


def test_document_choice_resolves_to_docx():
    spec = resolve_output_format("document")
    assert spec.format is OutputFormat.DOCUMENT
    assert spec.extension == ".docx"
    assert spec.media_type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


def test_docx_alias_is_accepted_for_compatibility():
    assert resolve_output_format("docx").format is OutputFormat.DOCUMENT


def test_unknown_format_is_rejected():
    with pytest.raises(ValueError):
        resolve_output_format("html")
