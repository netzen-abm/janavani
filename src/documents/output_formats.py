"""Shared output-format contract for Janavani document generation.

The content model is format-neutral. The user chooses the final artifact type:
- ``pdf``      -> Portable Document Format
- ``document`` -> editable Microsoft Word document (.docx)

Access surfaces must pass the user's choice into the shared document
capability. They must not implement format-specific business logic themselves.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class OutputFormat(str, Enum):
    PDF = "pdf"
    DOCUMENT = "document"

    @classmethod
    def parse(cls, value: str | "OutputFormat") -> "OutputFormat":
        if isinstance(value, cls):
            return value
        normalized = str(value).strip().lower().lstrip(".")
        aliases = {
            "pdf": cls.PDF,
            "document": cls.DOCUMENT,
            "doc": cls.DOCUMENT,
            "docx": cls.DOCUMENT,
        }
        try:
            return aliases[normalized]
        except KeyError as exc:
            raise ValueError(
                "Unsupported output format. User must choose 'pdf' or 'document'."
            ) from exc


@dataclass(frozen=True)
class OutputFormatSpec:
    """Rendering metadata for a user-selected output format."""

    format: OutputFormat
    extension: str
    media_type: str


OUTPUT_FORMATS: dict[OutputFormat, OutputFormatSpec] = {
    OutputFormat.PDF: OutputFormatSpec(
        OutputFormat.PDF,
        ".pdf",
        "application/pdf",
    ),
    OutputFormat.DOCUMENT: OutputFormatSpec(
        OutputFormat.DOCUMENT,
        ".docx",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ),
}


def resolve_output_format(value: str | OutputFormat) -> OutputFormatSpec:
    """Resolve the user's choice into a shared renderer specification."""

    selected = OutputFormat.parse(value)
    return OUTPUT_FORMATS[selected]
