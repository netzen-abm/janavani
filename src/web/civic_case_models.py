"""HTTP request/response models for the canonical civic-case adapter."""
from __future__ import annotations
from typing import Any
from pydantic import BaseModel, ConfigDict, Field
from src.core.civic_case import CaseType, CivicCase
from src.documents.document_contract import DocumentFormat

class CaseShellCreateRequest(BaseModel):
    """Create a Case lifecycle shell without transmitting citizen-authored content."""

    model_config = ConfigDict(extra="forbid")

    case_type: CaseType
    expected_vault_scope: str = Field(
        min_length=64, max_length=64, pattern=r"^[a-f0-9]{64}$"
    )


class CaseCreateRequest(BaseModel):
    case_type: CaseType
    subject: str = Field(min_length=1)
    narrative: str = Field(min_length=1)
    jurisdiction: dict[str, Any] = Field(default_factory=dict)
    related_organisation_id: str | None = None
    related_office_id: str | None = None
    related_official_id: str | None = None
    related_representative_id: str | None = None
    claims: list[dict[str, Any]] = Field(default_factory=list)

class ConsentRequest(BaseModel):
    consent_id: str = Field(min_length=1)


class ExplicitConsentRequest(BaseModel):
    scope: str = Field(default="citizen_download_and_self_send", min_length=1, max_length=120)
    explicit_confirmation: bool = False

class EvidenceRequest(BaseModel):
    evidence_id: str = Field(min_length=1)
    source_channel: str | None = None

class LetterDraftRequestModel(BaseModel):
    """Structured citizen input for the single shared civic drafting capability."""

    model_config = ConfigDict(extra="forbid")

    template_id: str = Field(min_length=1, max_length=120)
    template_version: int | None = Field(default=None, ge=1)
    subject: str = Field(min_length=1, max_length=500)
    issue: str = Field(min_length=1, max_length=20000)
    proposal_or_notice: str = Field(default="", max_length=12000)
    part_i_interrogatories: tuple[str, ...] = ()
    legal_framework: tuple[str, ...] = ()
    requested_conditions: tuple[str, ...] = ()
    requested_documents: tuple[str, ...] = ()
    remedies_reserved: tuple[str, ...] = ()
    references: tuple[str, ...] = ()
    evidence_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    response_period: str | None = Field(default=None, max_length=120)
    deadline_date: str | None = Field(default=None, max_length=40)
    jurisdiction: str | None = Field(default=None, max_length=500)
    language: str = Field(default="en", min_length=2, max_length=12)
    document_type: str = Field(default="Civic document", max_length=120)


class DocumentReviewRequestModel(BaseModel):
    document_id: str = Field(min_length=1)
    subject: str | None = None
    body: str | None = None
    reason: str | None = None

class ArtifactRequest(BaseModel):
    document_id: str = Field(min_length=1)
    document_format: DocumentFormat = DocumentFormat.PDF

class EventRequest(BaseModel):
    source_channel: str | None = None
    subject: str | None = None
    narrative: str | None = None
    source_ref: str | None = None
    notes: str | None = None

def event_result(case: CivicCase, event_type: str) -> dict[str, object]:
    return {"case_id": case.case_id, "status": case.status.value, "event": event_type}

def serialize_draft(draft, *, case_id: str, submission: str) -> dict[str, object]:
    return {
        "case_id": case_id, "document_id": draft.document_id,
        "document_type": draft.document_type, "date": draft.date,
        "subject": draft.subject, "body": draft.body,
        "to": {"name": draft.to.name, "address": draft.to.address, "email": draft.to.email, "role": draft.to.role},
        "cc": [{"name": p.name, "address": p.address, "email": p.email, "role": p.role} for p in draft.cc],
        "template_id": draft.template_id,
        "template_version": draft.template_version,
        "submission": submission,
    }

def serialize_case(case: CivicCase) -> dict[str, object]:
    return {
        "case_id": case.case_id, "case_type": case.case_type.value,
        "subject": case.subject, "narrative": case.narrative,
        "created_by": case.created_by, "jurisdiction": case.jurisdiction,
        "related_organisation_id": case.related_organisation_id,
        "related_office_id": case.related_office_id,
        "related_official_id": case.related_official_id,
        "related_representative_id": case.related_representative_id,
        "claims": list(case.claims), "evidence_refs": list(case.evidence_refs),
        "document_refs": list(case.document_refs), "consent_refs": list(case.consent_refs),
        "status": case.status.value,
        "events": [
            {"event_id": event.event_id, "event_type": event.event_type.value,
             "occurred_at": event.occurred_at, "actor_id": event.actor_id,
             "source_channel": event.source_channel, "source_ref": event.source_ref,
             "notes": event.notes}
            for event in case.events
        ],
    }
