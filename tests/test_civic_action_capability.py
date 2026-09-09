"""Renderer contract tests using the canonical civic-action capability."""

from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType
from src.documents.document_contract import DocumentFormat
from src.documents.renderers import render_document
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository


def identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="renderer-test-principal",
            interface="test",
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT", "case:write", "case:review"}),
        )
    )


def test_canonical_civic_action_draft_renders_to_pdf_and_docx(tmp_path) -> None:
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-2",
            name="Office",
            authority_type="office",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(
                name="Authority",
                address="Address",
                verified=True,
            ),
            verification_status="VERIFIED",
        )
    ])

    case = CivicCaseCapability(cases).create(
        CivicCaseCreateRequest(
            case_type=CaseType.REPRESENTATION,
            subject="Representation",
            narrative="Please consider this representation.",
            related_office_id="office-2",
        ),
        identity=identity(),
        source_channel="test",
    ).case

    case_capability = CivicCaseCapability(cases)
    action = CivicActionCapability(
        case_capability=case_capability,
        case_repository=cases,
        authority_repository=authorities,
    )
    draft = action.build_document(
        case.case_id,
        identity=identity(),
        document_id="doc-2",
        date="2026-09-03",
    ).draft

    pdf = render_document(draft, DocumentFormat.PDF, tmp_path)
    docx = render_document(draft, DocumentFormat.DOCX, tmp_path)

    assert pdf.exists()
    assert docx.exists()
    assert pdf.suffix == ".pdf"
    assert docx.suffix == ".docx"
