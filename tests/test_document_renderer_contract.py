from dataclasses import dataclass
from datetime import date

import pytest

from documents.document_contract import DocumentArtifact, StructuredDocument
from documents.renderers import RendererRegistry


@dataclass
class FakeRenderer:
    format: str = "pdf"
    media_type: str = "application/pdf"

    def render(self, document: StructuredDocument) -> DocumentArtifact:
        return DocumentArtifact(
            document_id=document.document_id,
            format=self.format,
            media_type=self.media_type,
            content=b"test",
            filename=f"{document.document_id}.pdf",
        )


def test_renderer_registry_is_format_driven() -> None:
    registry = RendererRegistry()
    renderer = FakeRenderer()
    registry.register(renderer)

    assert registry.get("PDF") is renderer
    assert registry.formats() == ("pdf",)


def test_unknown_renderer_is_explicit() -> None:
    with pytest.raises(ValueError, match="No renderer registered"):
        RendererRegistry().get("web3pdf")


def test_artifact_contract_normalizes_format() -> None:
    artifact = DocumentArtifact(
        document_id="JV-test",
        format="PDF",
        media_type="application/pdf",
        content=b"pdf",
        filename="JV-test.pdf",
    )
    assert artifact.format == "pdf"
