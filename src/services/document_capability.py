"""Privacy-first document capability.

Documents are composed from the minimum case data required for the selected
civic action. The capability is provider-neutral and never requires a server
copy of the citizen's personal data.
"""
from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Protocol
from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    case_id: str
    document_type: str = Field(min_length=2, max_length=100)
    facts: dict[str, Any] = Field(default_factory=dict)
    authority: dict[str, Any] = Field(default_factory=dict)
    user_content: dict[str, Any] = Field(default_factory=dict)
    format: str = "pdf"
    allow_external_processing: bool = False


class DocumentResult(BaseModel):
    ok: bool
    document_id: str | None = None
    content: str | None = None
    format: str | None = None
    provider: str | None = None
    provenance: list[dict[str, Any]] = Field(default_factory=list)
    error_code: str | None = None


class DocumentProvider(Protocol):
    name: str
    def supports(self, request: DocumentRequest) -> bool: ...
    def compose(self, request: DocumentRequest) -> DocumentResult: ...


@dataclass
class DocumentCapability:
    providers: list[DocumentProvider]

    def __init__(self, providers: list[DocumentProvider] | None = None) -> None:
        self.providers = providers or []

    def register(self, provider: DocumentProvider) -> None:
        self.providers.append(provider)

    def compose(self, request: DocumentRequest) -> DocumentResult:
        for provider in self.providers:
            if provider.supports(request):
                return provider.compose(request)
        return DocumentResult(ok=False, format=request.format, error_code="document_provider_unavailable")
