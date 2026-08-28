"""Pure domain-to-row serialization for the canonical SQL schema.

These helpers perform no I/O. They keep database column mapping deterministic
and make repository implementations testable without a live database.
"""

from __future__ import annotations

from typing import Any

from src.domain.authority import Authority
from src.domain.case import Case
from src.domain.consent import Consent
from src.domain.document import Document
from src.domain.evidence import Evidence
from src.domain.submission import Submission


def case_row(case: Case) -> dict[str, Any]:
    return {
        "id": case.id,
        "issue": case.issue,
        "status": case.status.value,
        "facts": case.facts,
    }


def evidence_row(evidence: Evidence) -> dict[str, Any]:
    return {
        "evidence_id": evidence.evidence_id,
        "case_id": evidence.case_id,
        "kind": evidence.kind.value,
        "title": evidence.title,
        "source": evidence.source,
        "status": evidence.status.value,
        "content_ref": evidence.content_ref,
        "captured_at": evidence.captured_at.isoformat() if evidence.captured_at else None,
        "metadata": evidence.metadata,
        "provenance": evidence.provenance,
    }


def authority_row(authority: Authority) -> dict[str, Any]:
    return {
        "authority_id": authority.authority_id,
        "name": authority.name,
        "authority_type": authority.authority_type,
        "organisation_id": authority.organisation_id,
        "office_id": authority.office_id,
        "jurisdiction": authority.jurisdiction,
        "postal_addresses": list(authority.postal_addresses),
        "contact_points": list(authority.contact_points),
        "official_urls": list(authority.official_urls),
        "source_refs": [
            {
                "source_id": source.source_id,
                "source_type": source.source_type,
                "uri": source.uri,
                "publisher": source.publisher,
                "retrieved_at": source.retrieved_at.isoformat() if source.retrieved_at else None,
                "version_or_reference": source.version_or_reference,
            }
            for source in authority.source_refs
        ],
        "verification_status": authority.verification_status.value,
        "last_verified_at": authority.last_verified_at.isoformat() if authority.last_verified_at else None,
    }


def consent_row(consent: Consent) -> dict[str, Any]:
    return {
        "consent_id": consent.consent_id,
        "subject_id": consent.subject_id,
        "capability_id": consent.capability_id,
        "purpose": consent.purpose,
        "scope": list(consent.scope),
        "data_categories": list(consent.data_categories),
        "grant_type": "explicit",
        "status": consent.status.value,
        "policy_version": consent.policy_version,
        "source_channel": consent.source_channel,
        "granted_at": consent.granted_at.isoformat(),
        "expires_at": consent.expires_at.isoformat() if consent.expires_at else None,
        "revoked_at": consent.revoked_at.isoformat() if consent.revoked_at else None,
        "proof_ref": consent.proof_ref,
    }


def _party_row(party: Any) -> dict[str, Any]:
    return {
        "party_type": party.party_type,
        "name": party.name,
        "postal_address": party.postal_address,
        "email": party.email,
        "phone": party.phone,
        "official_source_ref": party.official_source_ref,
    }


def document_row(document: Document) -> dict[str, Any]:
    return {
        "document_id": document.document_id,
        "case_id": document.case_id,
        "document_type": document.document_type.value,
        "title": document.title,
        "language": document.language,
        "subject": document.subject,
        "body": document.body,
        "from_party": _party_row(document.from_party) if document.from_party else None,
        "to_party": _party_row(document.to_party),
        "cc_parties": [_party_row(item) for item in document.cc_parties],
        "references_json": list(document.references),
        "enclosures": list(document.enclosures),
        "version": document.version,
        "status": document.status.value,
        "artifact_ref": document.artifact_ref,
        "content_hash": document.content_hash,
    }


def submission_row(submission: Submission) -> dict[str, Any]:
    return {
        "submission_id": submission.submission_id,
        "operation_id": submission.operation_id,
        "case_id": submission.case_id,
        "destination_ref": submission.destination_ref,
        "status": submission.status.value,
        "consent_ref": submission.consent_ref,
        "authorization_ref": submission.authorization_ref,
        "payload_hash": submission.payload_hash,
    }
