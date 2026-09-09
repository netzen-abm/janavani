from src.capabilities.civic_action_capability import CivicActionCapability
from src.capabilities.civic_action_vertical_slice import (
    CivicActionVerticalSlice,
    CivicActionVerticalSliceDependencies,
)
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseCreateRequest
from src.capabilities.document_review import DocumentReviewCapability, DocumentReviewRequest
from src.capabilities.evidence import EvidenceCapability, EvidenceCreateRequest
from src.capabilities.submission import SubmissionCapability, SubmissionReceipt, SubmissionRequest
from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.civic_case import CaseType
from src.core.evidence import EvidenceSource
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository
from src.storage.repositories.document_artifact import InMemoryDocumentArtifactRepository
from src.storage.repositories.document_review import InMemoryDocumentReviewRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def send(self, *, case, document_id: str, destination_ref: str) -> SubmissionReceipt:
        self.calls.append((case.case_id, document_id, destination_ref))
        return SubmissionReceipt(acknowledgement_ref="ACK-1", notes="Accepted by test transport")


def identity() -> IdentityContext:
    return IdentityContext(
        principal=Principal(
            principal_id="citizen-1",
            interface="test",
            capabilities=frozenset({
                "JNV-CIVIC-COMPLAINT", "case:write", "case:review",
                "case:evidence", "evidence:register", "evidence:read",
                "document:review", "case:submit",
            }),
        )
    )


def build_slice():
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-1",
            name="District Officer",
            authority_type="district",
            jurisdiction={"city": "Bengaluru"},
            primary_contact=AuthorityContact(name="District Officer", address="District Office"),
            verification_status="VERIFIED",
        )
    ])
    evidence = InMemoryEvidenceRepository()
    consents = InMemoryConsentRepository()
    reviews = InMemoryDocumentReviewRepository()
    artifacts = InMemoryDocumentArtifactRepository()
    transport = FakeTransport()

    case_capability = CivicCaseCapability(cases)
    evidence_capability = EvidenceCapability(evidence, case_capability)
    civic_action = CivicActionCapability(
        case_capability=case_capability,
        case_repository=cases,
        authority_repository=authorities,
        evidence_repository=evidence,
        artifact_repository=artifacts,
    )
    review = DocumentReviewCapability(reviews, case_capability=case_capability)
    submission = SubmissionCapability(case_capability, consents, transport)
    slice_ = CivicActionVerticalSlice(CivicActionVerticalSliceDependencies(
        case_capability=case_capability,
        civic_action_capability=civic_action,
        document_review_capability=review,
        submission_capability=submission,
        case_repository=cases,
        document_review_repository=reviews,
        artifact_repository=artifacts,
        evidence_repository=evidence,
    ))

    case = case_capability.create(
        CivicCaseCreateRequest(
            case_type=CaseType.COMPLAINT,
            subject="Road safety issue",
            narrative="A dangerous road condition needs correction.",
            related_office_id="office-1",
        ), identity=identity(), source_channel="test",
    ).case
    return slice_, evidence_capability, consents, transport, case


def test_complete_civic_action_path_uses_shared_boundaries():
    slice_, evidence_capability, consents, transport, case = build_slice()
    actor = identity()

    evidence = evidence_capability.register(EvidenceCreateRequest(
        evidence_type="photo",
        storage_ref="local://photo-1",
        sha256="a" * 64,
        received_at="2026-09-09T10:00:00Z",
        provenance=(EvidenceSource(source_id="capture-1", source_type="citizen"),),
    ), identity=actor)
    slice_.attach_evidence(case.case_id, evidence.evidence_id, identity=actor)

    consent = Consent(
        consent_id="consent-1",
        subject_id="citizen-1",
        purpose="case_submission",
        scope=("office:office-1",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-09T10:01:00Z",
    )
    consents.save(consent)
    slice_.add_consent(case.case_id, consent.consent_id, identity=actor)

    prepared = slice_.prepare_document(case.case_id, identity=actor, document_id="doc-1")
    edited = slice_.review_document(
        DocumentReviewRequest("doc-1", body="Corrected citizen narrative.", reason="Citizen correction"),
        identity=actor,
    )
    assert edited.body == "Corrected citizen narrative."
    assert prepared.document_id == "doc-1"

    slice_.start_review(case.case_id, identity=actor)
    ready = slice_.approve(case.case_id, identity=actor)
    assert ready.case.status.value == "READY"

    result = slice_.submit(
        SubmissionRequest(
            case_id=case.case_id,
            document_id="doc-1",
            destination_ref="office:office-1",
            consent_scope="office:office-1",
            source_channel="test",
        ),
        identity=actor,
        explicit_user_approval=True,
    )

    assert result.case.status.value == "ACKNOWLEDGED"
    assert result.case.events[-1].source_ref == "ACK-1"
    assert transport.calls == [(case.case_id, "doc-1", "office:office-1")]


def test_vertical_slice_cannot_submit_without_explicit_approval():
    slice_, _, consents, _, case = build_slice()
    actor = identity()
    consents.save(Consent(
        consent_id="consent-1", subject_id="citizen-1", purpose="case_submission",
        scope=("office:office-1",), grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED, created_at="2026-09-09T10:00:00Z",
    ))
    slice_.add_consent(case.case_id, "consent-1", identity=actor)
    slice_.prepare_document(case.case_id, identity=actor, document_id="doc-1")
    slice_.start_review(case.case_id, identity=actor)
    slice_.approve(case.case_id, identity=actor)

    import pytest
    with pytest.raises(PermissionError):
        slice_.submit(
            SubmissionRequest(case.case_id, "doc-1", "office:office-1", "office:office-1"),
            identity=actor,
            explicit_user_approval=False,
        )
