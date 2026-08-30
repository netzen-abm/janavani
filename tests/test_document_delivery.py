import pytest

from src.core.capabilities.document_delivery import SharedDocumentDelivery
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.document_delivery import DocumentAddress, DocumentFormat, DocumentStatus


def verified_authority():
    return AuthorityCandidate(
        "a1", "Verified Authority", "department", "IN-KL", "verified", ("official-1",),
        AuthorityStatus.VERIFIED, "Office Address", "office@example.gov.in", "CC Address", "cc@example.gov.in",
    )


def test_prepare_prefills_verified_to_and_cc_and_requires_review():
    doc = SharedDocumentDelivery().prepare(
        case_id="JV-1", document_type="complaint", content="Please address this issue.",
        authority=verified_authority(), format=DocumentFormat.PDF,
    )
    assert doc.to.email == "office@example.gov.in"
    assert doc.cc[0].email == "cc@example.gov.in"
    assert doc.status == DocumentStatus.USER_REVIEW


def test_unverified_authority_cannot_prepare_document():
    authority = verified_authority()
    authority = AuthorityCandidate(authority.authority_id, authority.name, authority.authority_type, authority.jurisdiction, authority.reason, (), AuthorityStatus.CANDIDATE, authority.to_address, authority.to_email)
    with pytest.raises(ValueError):
        SharedDocumentDelivery().prepare(case_id="JV-1", document_type="complaint", content="x", authority=authority, format=DocumentFormat.DOCX)


def test_user_can_correct_content_and_recipient_then_approve_and_deliver():
    service = SharedDocumentDelivery()
    doc = service.prepare(case_id="JV-1", document_type="complaint", content="old", authority=verified_authority(), format=DocumentFormat.DOCX)
    doc = service.revise(doc, content="corrected", to=DocumentAddress("Corrected Office", "New Address", "new@example.gov.in"))
    doc = service.approve(doc)
    doc = service.deliver(doc)
    assert doc.content == "corrected"
    assert doc.to.email == "new@example.gov.in"
    assert doc.status == DocumentStatus.DELIVERED
