"""Shared citizen document review/correction capability.

Corrections are proposed changes, never automatically treated as verified truth.
The capability keeps a revision and verification state so learning systems can
consume verified corrections without turning arbitrary user edits into facts.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional
from uuid import uuid4

from src.core.capabilities.document_preparation import DocumentDraft


class CorrectionVerification(str, Enum):
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass(frozen=True)
class DocumentCorrection:
    correction_id: str
    document_id: str
    field: str
    old_value: str
    new_value: str
    source: str = "citizen"
    verification: CorrectionVerification = CorrectionVerification.PENDING
    reason: Optional[str] = None


@dataclass(frozen=True)
class DocumentReview:
    document_id: str
    corrections: tuple[DocumentCorrection, ...] = ()
    approved: bool = False


class SharedDocumentReview:
    """Create review revisions without silently mutating canonical facts."""

    EDITABLE_FIELDS = frozenset({
        "to_name", "to_address", "to_email",
        "cc_name", "cc_address", "cc_email",
        "subject", "body",
    })

    def propose_correction(
        self,
        draft: DocumentDraft,
        *,
        field: str,
        new_value: str,
        reason: Optional[str] = None,
    ) -> DocumentCorrection:
        if field not in self.EDITABLE_FIELDS:
            raise ValueError(f"Field is not editable: {field}")
        old_value = getattr(draft, field)
        old_text = "" if old_value is None else str(old_value)
        new_text = "" if new_value is None else str(new_value)
        return DocumentCorrection(
            correction_id=f"corr-{uuid4().hex[:16]}",
            document_id=draft.document_id,
            field=field,
            old_value=old_text,
            new_value=new_text,
            reason=reason,
        )

    @staticmethod
    def apply_local_revision(draft: DocumentDraft, corrections: tuple[DocumentCorrection, ...]) -> DocumentDraft:
        """Apply citizen edits to a local draft; verification remains separate."""
        values = {field: getattr(draft, field) for field in SharedDocumentReview.EDITABLE_FIELDS}
        for correction in corrections:
            if correction.document_id != draft.document_id:
                raise ValueError("Correction belongs to a different document")
            if correction.field not in SharedDocumentReview.EDITABLE_FIELDS:
                raise ValueError(f"Field is not editable: {correction.field}")
            values[correction.field] = correction.new_value or None
        return DocumentDraft(
            document_id=draft.document_id,
            document_type=draft.document_type,
            to_name=values["to_name"] or "",
            to_address=values["to_address"] or "",
            to_email=values["to_email"],
            cc_name=values["cc_name"],
            cc_address=values["cc_address"],
            cc_email=values["cc_email"],
            subject=values["subject"] or "",
            body=values["body"] or "",
            source_case_id=draft.source_case_id,
            editable=draft.editable,
            submission_enabled=False,
            metadata=draft.metadata,
        )
