"""Channel-neutral shared Document capability.

Document composition is separated from rendering and delivery. Providers are
replaceable and access surfaces must not own document business logic.
"""

from dataclasses import dataclass, field
from typing import Any, Protocol

DOCUMENT_SCHEMA_VERSION = 1
SUPPORTED_TYPES = {"complaint", "grievance", "rti", "petition", "representation"}
SUPPORTED_FORMATS = {"pdf", "docx", "text"}


@dataclass(frozen=True)
class DocumentRequest:
    case_id: str
    document_type: str
    data: dict[str, Any] = field(default_factory=dict)
    output_format: str = "pdf"
    allow_external_processing: bool = False


@dataclass(frozen=True)
class DocumentArtifact:
    schema_version: int
    document_id: str
    case_id: str
    document_type: str
    output_format: str
    content: bytes | str
    provider: str
    status: str = "generated"


class DocumentProvider(Protocol):
    name: str

    def generate(self, request: DocumentRequest) -> DocumentArtifact:
        """Generate a document without owning channel or case storage."""


class DocumentCapability:
    """Routes document generation to a registered provider."""

    def __init__(self, providers: dict[str, DocumentProvider] | None = None):
        self._providers = providers or {}

    def register(self, provider: DocumentProvider) -> None:
        if not provider.name:
            raise ValueError("Document provider name is required")
        self._providers[provider.name] = provider

    def generate(self, request: DocumentRequest, provider: str | None = None) -> DocumentArtifact:
        if not request.case_id:
            raise ValueError("case_id is required")
        if request.document_type not in SUPPORTED_TYPES:
            raise ValueError(f"Unsupported document type: {request.document_type}")
        if request.output_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported output format: {request.output_format}")
        if not self._providers:
            raise RuntimeError("No document provider is registered")
        selected = self._providers.get(provider) if provider else next(iter(self._providers.values()))
        if selected is None:
            raise ValueError(f"Unknown document provider: {provider}")
        return selected.generate(request)
