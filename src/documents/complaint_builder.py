"""Canonical complaint document builder.

The builder creates channel-neutral structured data. Rendering and delivery
are separate capabilities so Web, mobile, messaging, DApp and future clients
can use the same document contract independently.
"""

from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4
from typing import Any

from documents.document_contract import DocumentRequest, StructuredDocument
from documents.legal_enrichment import LegalEnricher, enrich_document


def build_complaint(
    user_name: str,
    user_address: str,
    office_id: str,
    issue_text: str,
    *,
    language: str = "en",
    legal_enricher: LegalEnricher | None = None,
) -> StructuredDocument:
    """Build a structured complaint without rendering or delivery side effects.

    Legal analysis is optional enrichment. A provider failure never prevents
    deterministic document composition.
    """
    request = DocumentRequest(
        document_type="complaint",
        user_name=user_name,
        user_address=user_address,
        office_id=office_id,
        issue_text=issue_text,
        language=language,
    )
    created_at = datetime.now(timezone.utc)
    document_id = f"JV-{created_at:%Y%m%d}-{uuid4().hex[:12]}"
    legal_analysis = enrich_document(request.issue_text, enricher=legal_enricher)
    provenance: dict[str, Any] = {
        "builder": "documents.complaint_builder.build_complaint",
        "generated_at": created_at.isoformat(),
        "legal_enrichment": "available" if legal_analysis is not None else "unavailable",
    }
    return StructuredDocument(
        document_type=request.document_type,
        document_id=document_id,
        created_on=date.today(),
        content={
            "date": created_at.date().isoformat(),
            "user": {"name": request.user_name, "address": request.user_address},
            "office_id": request.office_id,
            "issue": request.issue_text,
            "language": request.language,
        },
        legal_analysis=legal_analysis,
        provenance=provenance,
    )
