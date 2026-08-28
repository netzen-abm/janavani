"""Pure SQL-row-to-domain hydration for canonical records.

The functions validate required fields and reconstruct domain objects without
database I/O. They are intentionally explicit so schema drift fails at the
storage boundary instead of leaking malformed state into the domain.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from src.domain.authority import Authority, AuthoritySource, AuthorityVerificationStatus
from src.domain.case import Case, CaseStatus
from src.domain.consent import Consent, ConsentStatus
from src.domain.document import Document, DocumentStatus, DocumentType, PartyRef
from src.domain.evidence import Evidence, EvidenceKind, EvidenceStatus
from src.domain.submission import Submission, SubmissionStatus


def _required(row: dict[str, Any], key: str) -> Any:
    value = row.get(key)
    if value is None:
        raise ValueError(f"missing required database field: {key}")
    return value


def _dt(value: Any) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def case_from_row(row: dict[str, Any]) -> Case:
    return Case(
        id=str(_required(row, "id")),
        issue=str(_required(row, "issue")),
        status=CaseStatus(str(row.get("status", CaseStatus.OPEN.value))),
        facts=dict(row.get("facts") or {}),
    )


def evidence_from_row(row: dict[str, Any]) -> Evidence:
    return Evidence(
        evidence_id=str(_required(row, "evidence_id")),
        case_id=str(_required(row, "case_id")),
        kind=EvidenceKind(str(_required(row, "kind"))),
        title=str(_required(row, "title")),
        source=str(_required(row, "source")),
        status=EvidenceStatus(str(row.get("status", EvidenceStatus.PROVIDED.value))),
        content_ref=row.get("content_ref"),
        captured_at=_dt(row.get("captured_at")),
        metadata=dict(row.get("metadata") or {}),
        provenance=list(row.get("provenance") or []),
    )


def authority_from_row(row: dict[str, Any]) -> Authority:
    sources = [
        AuthoritySource(
            source_id=str(_required(source, "source_id")),
            source_type=str(_required(source, "source_type")),
            uri=str(_required(source, "uri")),
            publisher=source.get("publisher"),
            retrieved_at=_dt(source.get("retrieved_at")),
            version_or_reference=source.get("version_or_reference"),
        )
        for source in (row.get("source_refs") or [])
    ]
    return Authority(
        authority_id=str(_required(row, "authority_id")),
        name=str(_required(row, "name")),
        authority_type=str(_required(row, "authority_type")),
        organisation_id=row.get("organisation_id"),
        office_id=row.get("office_id"),
        jurisdiction=dict(row.get("jurisdiction") or {}),
        postal_addresses=list(row.get("postal_addresses") or []),
        contact_points=list(row.get("contact_points") or []),
        official_urls=list(row.get("official_urls") or []),
        source_refs=sources,
        verification_status=AuthorityVerificationStatus(str(row.get("verification_status", "unverified"))),
        last_verified_at=_dt(row.get("last_verified_at")),
    )


def consent_from_row(row: dict[str, Any]) -> Consent:
    return Consent(
        consent_id=str(_required(row, "consent_id")),
        subject_id=str(_required(row, "subject_id")),
        capability_id=str(_required(row, "capability_id")),
        purpose=str(_required(row, "purpose")),
        scope=tuple(str(x) for x in (row.get("scope") or [])),
        data_categories=tuple(str(x) for x in (row.get("data_categories") or [])),
        status=ConsentStatus(str(_required(row, "status"))),
        policy_version=str(_required(row, "policy_version")),
        source_channel=str(_required(row, "source_channel")),
        granted_at=_dt(_required(row, "granted_at")),
        expires_at=_dt(row.get("expires_at")),
        revoked_at=_dt(row.get("revoked_at")),
        proof_ref=row.get("proof_ref"),
    )


def _party_from_row(value: Any) -> PartyRef:
    if not isinstance(value, dict):
        raise ValueError("document party must be an object")
    return PartyRef(
        party_type=str(_required(value, "party_type")),
        name=str(_required(value, "name")),
        postal_address=value.get("postal_address"),
        email=value.get("email"),
        phone=value.get("phone"),
        official_source_ref=value.get("official_source_ref"),
    )


def document_from_row(row: dict[str, Any]) -> Document:
    return Document(
        document_id=str(_required(row, "document_id")),
        document_type=DocumentType(str(_required(row, "document_type"))),
        title=str(_required(row, "title")),
        language=str(_required(row, "language")),
        to_party=_party_from_row(_required(row, "to_party")),
        subject=str(_required(row, "subject")),
        body=str(_required(row, "body")),
        from_party=PartyRef(**row["from_party"]) if row.get("from_party") else None,
        cc_parties=tuple(PartyRef(**item) for item in (row.get("cc_parties") or [])),
        references=tuple(str(x) for x in (row.get("references_json") or [])),
        enclosures=tuple(str(x) for x in (row.get("enclosures") or [])),
        version=int(row.get("version", 1)),
        status=DocumentStatus(str(row.get("status", DocumentStatus.DRAFT.value))),
        case_id=row.get("case_id"),
        artifact_ref=row.get("artifact_ref"),
        content_hash=row.get("content_hash"),
        created_at=_dt(row.get("created_at")) or datetime.now(timezone.utc),
        updated_at=_dt(row.get("updated_at")) or datetime.now(timezone.utc),
    )


def submission_from_row(row: dict[str, Any]) -> Submission:
    return Submission(
        submission_id=str(_required(row, "submission_id")),
        operation_id=str(_required(row, "operation_id")),
        case_id=str(_required(row, "case_id")),
        destination_ref=str(_required(row, "destination_ref")),
        status=SubmissionStatus(str(row.get("status", SubmissionStatus.CREATED.value))),
        consent_ref=row.get("consent_ref"),
        authorization_ref=row.get("authorization_ref"),
        payload_hash=row.get("payload_hash"),
    )
