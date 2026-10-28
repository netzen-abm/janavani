"""Stable value objects for reusable civic-document templates."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class TemplateSection:
    """Named layout slot plus optional generic, reviewed starter wording."""

    field_name: str
    heading: str
    default_items: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class CivicDocumentTemplate:
    """Versioned structural model; never stores a citizen's document values."""

    template_id: str
    version: int
    title: str
    document_type: str
    purpose: str
    jurisdiction_scope: str
    language: str
    compatible_case_types: tuple[str, ...]
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    sections: tuple[TemplateSection, ...]
    introduction: str
    provenance: str = "Janavani structural model; verify all legal citations and procedures."
    review_status: str = "structural-only"
