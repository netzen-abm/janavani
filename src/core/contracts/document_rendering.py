"""Channel-neutral document rendering contract.

Rendering is a pure output concern. It accepts an already reviewed draft and
returns a local output artifact. It never sends, emails, submits, queries a
database, or fetches additional personal data.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from src.core.capabilities.document_preparation import DocumentDraft


class DocumentFormat(str, Enum):
    PDF = "pdf"
    DOCX = "docx"


@dataclass(frozen=True)
class RenderedDocument:
    document_id: str
    format: DocumentFormat
    output_path: str
    submission_enabled: bool = False


class DocumentRenderer(Protocol):
    format: DocumentFormat

    def render(self, draft: DocumentDraft, output_path: str) -> RenderedDocument: ...
