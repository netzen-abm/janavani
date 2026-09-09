import pytest

from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.document_review import DocumentReviewCapability, DocumentReviewRequest
from src.core.civic_case import CaseType
from src.documents.document_contract import DocumentDraft, DocumentParty
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.document_review import InMemoryDocumentReviewRepository


def identity(principal_id: str = "owner", *, review: bool = True) -> IdentityContext:
    caps = {"JNV-CIVIC-COMPLAINT", "case:write"}
    if review:
        caps.add("document:review")
    return IdentityContext(principal=Principal(
        principal_id=principal_id, interface="test", capabilities=frozenset(caps)
    ))


def setup():
    cases = InMemoryCivicCaseRepository()
    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(CaseType.COMPLAINT, "Subject", "Narrative"),
        identity=identity(),
    ).case
    draft = DocumentDraft(
        document_id="doc-1", document_type="representation", case_id=case.case_id,
        date="2026-09-09", subject="Original", body="Original body",
        to=DocumentParty(name="District Officer", address="Office"),
    )
    case.document_refs.append(draft.document_id)
    cases.save(case)
    docs = InMemoryDocumentReviewRepository()
    docs.save(draft)
    return cases, docs, case, draft


def test_shared_capability_edits_owned_attached_draft():
    cases, docs, case, _ = setup()
    capability = DocumentReviewCapability(docs, case_capability=CivicCaseCapability(cases))

    edited = capability.edit(
        DocumentReviewRequest("doc-1", subject="Corrected", reason="Citizen correction"),
        identity=identity(),
    )

    assert edited.subject == "Corrected"
    assert docs.get("doc-1").subject == "Corrected"
    assert docs.revisions("doc-1")[0].case_id == case.case_id


def test_cross_owner_cannot_edit_attached_draft():
    cases, docs, case, _ = setup()
    capability = DocumentReviewCapability(docs, case_capability=CivicCaseCapability(cases))

    with pytest.raises(LookupError):
        capability.edit(DocumentReviewRequest("doc-1", body="Tampered"), identity=identity("other"))


def test_document_review_requires_capability():
    cases, docs, _, _ = setup()
    capability = DocumentReviewCapability(docs, case_capability=CivicCaseCapability(cases))

    with pytest.raises(PermissionError):
        capability.edit(DocumentReviewRequest("doc-1", body="No permission"), identity=identity(review=False))
