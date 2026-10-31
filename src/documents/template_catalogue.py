"""Versioned catalogue lookup for approved civic-document structure."""
from __future__ import annotations

from src.documents.template_models import CivicDocumentTemplate, TemplateSection
from src.documents.template_definitions import _TEMPLATES

__all__ = [
    "CivicDocumentTemplate",
    "TemplateSection",
    "TemplateNotFoundError",
    "list_templates",
    "get_template",
]


class TemplateNotFoundError(LookupError):
    """Unknown template ID/version."""


def list_templates(*, language: str | None = None) -> tuple[CivicDocumentTemplate, ...]:
    """Return immutable catalogue definitions, optionally filtered by language."""
    templates = _TEMPLATES
    if language is not None:
        normalized = language.strip().lower()
        templates = tuple(item for item in templates if item.language == normalized)
    return templates


def get_template(
    template_id: str,
    *,
    version: int | None = None,
    language: str = "en",
) -> CivicDocumentTemplate:
    """Resolve an approved version. Unknown IDs/versions fail closed."""
    key = template_id.strip().lower()
    locale = language.strip().lower()
    matches = [
        item for item in _TEMPLATES
        if item.template_id == key and item.language == locale
        and (version is None or item.version == version)
    ]
    if not matches:
        raise TemplateNotFoundError(f"Unsupported civic document template: {key}")
    return max(matches, key=lambda item: item.version)
