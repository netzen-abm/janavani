"""Application service for channel-neutral civic document generation."""

from __future__ import annotations

from documents.complaint_builder import build_complaint
from documents.document_contract import DocumentArtifact
from documents.renderers import RendererRegistry


_DEFAULT_RENDERERS = RendererRegistry()


def generate_complaint_document(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    format_type: str = "pdf",
    *,
    language: str = "en",
    renderer_registry: RendererRegistry | None = None,
) -> DocumentArtifact:
    """Compose a complaint and render it through the selected format contract.

    Composition, legal enrichment and rendering are separated. The caller gets
    a channel-neutral artifact and decides how/where it is delivered.
    """
    document = build_complaint(
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
        language=language,
    )
    registry = renderer_registry or _DEFAULT_RENDERERS
    return registry.get(format_type).render(document)
