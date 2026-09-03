"""Contract tests for Case -> Authority -> Evidence -> Document composition."""
from src.capabilities.civic_action import build_document_draft
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.civic_case import CaseType, CivicCase
from src.core.evidence import EvidenceObject
from src.documents.document_contract import DocumentFormat
from src.documents.renderers import render_document
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository


def test_civic_action_builds_document_from_canonical_authority() -> None:
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-1",
            name="District Office",
            authority_type="district",
            jurisdiction={"city": "Kochi"},
            primary_contact=AuthorityContact(
                name="District Officer",
                address="Official Office Address",
                email="office@example.gov.in",
                role="District Officer",
                source_ref="source-1",
                verified=True,
            ),
            verification_status="VERIFIED",
        )
    ])
    evidence = InMemoryEvidenceRepository()
    evidence.save(EvidenceObject(
        evidence_id="evidence-1",
        evidence_type="DOCUMENT",
        storage_ref="object://evidence-1",
        sha256="a" * 64,
        received_at="2026-09-03T00:00:00Z",
    ))
    case = CivicCase(
        case_id="case-1",
        case_type=CaseType.COMPLAINT,
        subject="Service issue",
        narrative="The service was not provided.",
        related_office_id="office-1",
        evidence_refs=["evidence-1"],
    )

    draft = build_document_draft(
        case,
        document_id="doc-1",
        date="2026-09-03",
        authority_repository=authorities,
        evidence_repository=evidence,
    )

    assert draft.case_id == "case-1"
    assert draft.to.email == "office@example.gov.in"
    assert draft.subject == "Service issue"

    case.add_document("doc-1", event_id="event-doc-1", occurred_at="2026-09-03T00:01:00Z")
    assert case.document_refs == ["doc-1"]
    assert case.events[-1].source_ref == "doc-1"


def test_civic_action_rejects_missing_evidence() -> None:
    case = CivicCase(
        case_id="case-3",
        case_type=CaseType.COMPLAINT,
        subject="Service issue",
        narrative="The service was not provided.",
        related_office_id="office-1",
        evidence_refs=["missing"],
    )
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-1",
            name="Office",
            authority_type="office",
            primary_contact=AuthorityContact(name="Authority", address="Address"),
        )
    ])

    try:
        build_document_draft(
            case,
            document_id="doc-3",
            date="2026-09-03",
            authority_repository=authorities,
            evidence_repository=InMemoryEvidenceRepository(),
        )
    except ValueError as exc:
        assert "missing evidence" in str(exc)
    else:
        raise AssertionError("Expected missing evidence to be rejected")


def test_renderer_contract_supports_pdf_and_docx(tmp_path) -> None:
    draft = build_document_draft(
        CivicCase(
            case_id="case-2",
            case_type=CaseType.REPRESENTATION,
            subject="Representation",
            narrative="Please consider this representation.",
            related_office_id="office-2",
        ),
        document_id="doc-2",
        date="2026-09-03",
        authority_repository=InMemoryAuthorityRepository([
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
        ]),
    )

    pdf = render_document(draft, DocumentFormat.PDF, tmp_path)
    docx = render_document(draft, DocumentFormat.DOCX, tmp_path)

    assert pdf.exists()
    assert docx.exists()
    assert pdf.suffix == ".pdf"
    assert docx.suffix == ".docx"
