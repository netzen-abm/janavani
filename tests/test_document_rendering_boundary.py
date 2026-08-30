import pytest

from src.core.capabilities.document_rendering import SharedDocumentRendering
from src.core.contracts.document_rendering import DocumentFormat


class FakeRenderer:
    def __init__(self, fmt):
        self.format = fmt

    def render(self, draft, output_path):
        from src.core.contracts.document_rendering import RenderedDocument
        return RenderedDocument(draft.document_id, self.format, output_path)


class Draft:
    document_id = "doc-1"
    editable = True
    submission_enabled = False


def test_render_requires_explicit_document_format(tmp_path):
    service = SharedDocumentRendering([FakeRenderer(DocumentFormat.PDF)])
    with pytest.raises(ValueError, match="explicitly selected"):
        service.render(Draft(), "pdf", str(tmp_path / "x.pdf"))
