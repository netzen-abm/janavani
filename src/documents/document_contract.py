"""Canonical contracts for Janavani document capabilities.

This module contains capability-level data contracts only. It does not own
channel logic, persistence, network delivery, or AI provider integration.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Mapping


SUPPORTED_DOCUMENT_TYPES = frozenset({"complaint", "rti", "petition", "grievance"})
SUPPORTED_FORMATS = frozenset({"pdf", "docx"})


@dataclass(frozen=True)
class DocumentRequest:
    """User-authorized request for a purpose-bound civic document."""

    document_type: str
    user_name: str
    user_address: str
    office_id: str
    issue_text: str
    language: str = "en"
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        normalized_type = self.document_type.strip().lower()
        if normalized_type not in SUPPORTED_DOCUMENT_TYPES:
            raise ValueError(f"Unsupported document type: {self.document_type}")
        if not self.issue_text.strip():
            raise ValueError("issue_text must not be empty")
        object.__setattr__(self, "document_type", normalized_type)


@dataclass(frozen=True)
class StructuredDocument:
    """Channel-neutral structured document ready for rendering."""

    document_type: str
    document_id: str
    created_on: date
    content: Mapping[str, Any]
    legal_analysis: Mapping[str, Any] | None = None
    provenance: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DocumentArtifact:
    """Rendered document artifact returned to any independent interface."""

    document_id: str
    format: str
    media_type: str
    content: bytes
    filename: str

    def __post_init__(self) -> None:
        normalized_format = self.format.strip().lower()
        if normalized_format not in SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported document format: {self.format}")
        object.__setattr__(self, "format", normalized_format)
