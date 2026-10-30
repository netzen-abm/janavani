"""Privacy-safe citizen-owned structural format models for civic documents."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from uuid import uuid4

from src.documents.template_catalogue import get_template


@dataclass(frozen=True, slots=True)
class CitizenDocumentFormat:
    """A canonical template reference plus approved section identifiers only."""

    format_id: str
    owner_principal_id: str
    template_id: str
    template_version: int
    section_field_names: tuple[str, ...]
    structure_hash: str
    created_at: str
    updated_at: str


def canonical_section_fields(
    template_id: str, template_version: int, field_names: tuple[str, ...] | list[str]
) -> tuple[str, ...]:
    """Validate and order only known structure IDs; never accept source prose."""
    template = get_template(template_id, version=template_version)
    selected = tuple(field_names)
    if not selected or any(not isinstance(value, str) or not value for value in selected):
        raise ValueError("Choose at least one reusable section")
    if len(set(selected)) != len(selected):
        raise ValueError("Duplicate section identifiers are not allowed")
    available = {section.field_name for section in template.sections}
    unknown = set(selected) - available
    if unknown:
        raise ValueError("Unsupported section identifier")
    required_sections = set(template.required_fields) & available
    if not required_sections.issubset(selected):
        raise ValueError("The selected format must retain all required document sections")
    return tuple(section.field_name for section in template.sections if section.field_name in set(selected))


def create_citizen_document_format(
    *,
    owner_principal_id: str,
    template_id: str,
    template_version: int,
    section_field_names: tuple[str, ...] | list[str],
) -> CitizenDocumentFormat:
    """Create a format record from canonical structure, never from draft content."""
    if not isinstance(owner_principal_id, str) or not owner_principal_id.strip():
        raise ValueError("An authenticated owner is required")
    template = get_template(template_id, version=template_version)
    sections = canonical_section_fields(template.template_id, template.version, section_field_names)
    canonical = json.dumps(
        {"template_id": template.template_id, "template_version": template.version, "sections": sections},
        ensure_ascii=True,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")
    digest = hashlib.sha256(canonical).hexdigest()
    now = datetime.now(timezone.utc).isoformat()
    return CitizenDocumentFormat(
        format_id=uuid4().hex,
        owner_principal_id=owner_principal_id,
        template_id=template.template_id,
        template_version=template.version,
        section_field_names=sections,
        structure_hash=digest,
        created_at=now,
        updated_at=now,
    )


def public_format_model(record: CitizenDocumentFormat) -> dict[str, object]:
    """Return only the structural model; never return the opaque owner identity."""
    template = get_template(record.template_id, version=record.template_version)
    headings = {section.field_name: section.heading for section in template.sections}
    return {
        "format_id": record.format_id,
        "template_id": record.template_id,
        "template_version": record.template_version,
        "section_field_names": list(record.section_field_names),
        "sections": [
            {"field_name": name, "heading": headings[name]}
            for name in record.section_field_names
        ],
        "created_at": record.created_at,
        "updated_at": record.updated_at,
    }
