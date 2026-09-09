import base64
import hashlib
import hmac
import json
import os
import time

import pytest
from fastapi.testclient import TestClient

from src.core.authority import AuthorityContact, AuthorityRecord
from src.core.consent import Consent, ConsentGrantType, ConsentStatus
from src.core.evidence import EvidenceObject, EvidenceSource
from src.platform.composition import create_civic_action_vertical_slice
from src.storage.repositories.authority import InMemoryAuthorityRepository
from src.storage.repositories.civic_case import InMemoryCivicCaseRepository
from src.storage.repositories.consent import InMemoryConsentRepository
from src.storage.repositories.document_artifact import InMemoryDocumentArtifactRepository
from src.storage.repositories.document_review import InMemoryDocumentReviewRepository
from src.storage.repositories.evidence import InMemoryEvidenceRepository
from src.web import civic_case_router
from src.web.canonical_app import app


SECRET = "test-identity-secret"
client = TestClient(app)


def _auth_header(principal_id: str = "principal-1") -> dict[str, str]:
    now = int(time.time())
    payload = {
        "iss": "janavani-identity", "aud": "janavani-api", "sub": principal_id,
        "provider": "test-identity", "subject": principal_id, "principal_id": principal_id,
        "authentication_method": "passkey", "iat": now, "exp": now + 60,
        "jti": f"web-e2e-{principal_id}-{now}",
        "capabilities": [
            "JNV-CIVIC-COMPLAINT", "case:read", "case:write", "case:review",
            "case:evidence", "case:submit", "evidence:register", "evidence:read",
            "document:review",
        ],
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    signature = hmac.new(SECRET.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return {"Authorization": f"Bearer {encoded}.{signed}"}


@pytest.fixture()
def web_state(monkeypatch):
    cases = InMemoryCivicCaseRepository()
    authorities = InMemoryAuthorityRepository([
        AuthorityRecord(
            authority_id="office-e2e",
            name="District Officer",
            authority_type="district",
            jurisdiction={"city": "Bengaluru"},
            primary_contact=AuthorityContact(
                name="District Officer", address="District Office", email="office@example.test", role="District Officer"
            ),
            verification_status="VERIFIED",
        )
    ])
    evidence = InMemoryEvidenceRepository()
    consents = InMemoryConsentRepository()
    reviews = InMemoryDocumentReviewRepository()
    artifacts = InMemoryDocumentArtifactRepository()
    composition = civic_case_router.create_web_civic_action_composition(
        case_repository=cases,
        authority_repository=authorities,
        evidence_repository=evidence,
        consent_repository=consents,
        document_review_repository=reviews,
        artifact_repository=artifacts,
    )
    monkeypatch.setattr(civic_case_router, "_REPOSITORY", cases)
    monkeypatch.setattr(civic_case_router, "_EVIDENCE_REPOSITORY", evidence)
    monkeypatch.setattr(civic_case_router, "_COMPOSITION", composition)
    monkeypatch.setattr(civic_case_router, "_CAPABILITY", composition.case_capability)
    monkeypatch.setattr(civic_case_router, "_CIVIC_ACTION", composition.civic_action)
    os.environ["JANAVANI_IDENTITY_ASSERTION_SECRET"] = SECRET
    return cases, evidence, consents, reviews, artifacts


def test_web_completes_case_evidence_consent_document_review_and_artifact(web_state):
    cases, evidence, consents, reviews, artifacts = web_state
    headers = _auth_header()

    created = client.post(
        "/civic/cases", headers=headers,
        json={
            "case_type": "complaint",
            "subject": "Unsafe road condition",
            "narrative": "The road requires urgent repair.",
            "related_office_id": "office-e2e",
        },
    )
    assert created.status_code == 200
    case_id = created.json()["case_id"]

    evidence.save(EvidenceObject(
        evidence_id="evidence-e2e",
        evidence_type="photo",
        storage_ref="local://e2e-photo",
        sha256="a" * 64,
        received_at="2026-09-09T10:00:00Z",
        provenance=(EvidenceSource(source_id="capture-e2e", source_type="citizen"),),
    ))
    attached = client.post(
        f"/civic/cases/{case_id}/evidence", headers=headers,
        json={"evidence_id": "evidence-e2e", "source_channel": "webapp"},
    )
    assert attached.status_code == 200
    assert attached.json()["event"] == "evidence_added"

    consents.save(Consent(
        consent_id="consent-e2e",
        subject_id="principal-1",
        purpose="case_submission",
        scope=("office:office-e2e",),
        grant_type=ConsentGrantType.EXPLICIT,
        status=ConsentStatus.GRANTED,
        created_at="2026-09-09T10:01:00Z",
    ))
    consent = client.post(
        f"/civic/cases/{case_id}/consent", headers=headers,
        json={"consent_id": "consent-e2e"},
    )
    assert consent.status_code == 200

    draft = client.get(f"/civic/cases/{case_id}/document/draft", headers=headers)
    assert draft.status_code == 200
    document_id = draft.json()["document_id"]
    assert draft.json()["to"]["name"] == "District Officer"

    reviewed = client.post(
        f"/civic/cases/{case_id}/document/review", headers=headers,
        json={"document_id": document_id, "body": "Corrected citizen narrative.", "reason": "Citizen correction"},
    )
    assert reviewed.status_code == 200
    assert reviewed.json()["body"] == "Corrected citizen narrative."
    assert reviews.get(document_id).body == "Corrected citizen narrative."

    started = client.post(f"/civic/cases/{case_id}/review", headers=headers, json={})
    assert started.status_code == 200 and started.json()["status"] == "review"
    ready = client.post(f"/civic/cases/{case_id}/ready", headers=headers, json={})
    assert ready.status_code == 200 and ready.json()["status"] == "ready"

    artifact = client.post(
        f"/civic/cases/{case_id}/document/artifact", headers=headers,
        json={"document_id": document_id, "document_format": "pdf"},
    )
    assert artifact.status_code == 200
    artifact_body = artifact.json()
    assert artifact_body["case_id"] == case_id
    assert artifact_body["document_id"] == document_id
    assert artifact_body["format"] == "pdf"
    assert artifact_body["submission"] == "not_submitted"
    assert artifacts.get(artifact_body["artifact_id"]) is not None

    final_case = client.get(f"/civic/cases/{case_id}", headers=headers)
    assert final_case.status_code == 200
    body = final_case.json()
    assert body["status"] == "ready"
    assert "evidence-e2e" in body["evidence_refs"]
    assert document_id in body["document_refs"]
    assert artifact_body["artifact_id"] in body["document_refs"]

    direct_submit = client.post(f"/civic/cases/{case_id}/submit", headers=headers, json={})
    assert direct_submit.status_code == 409


def test_web_ready_fails_closed_without_submission_consent(web_state):
    cases, _, _, _, _ = web_state
    headers = _auth_header()
    created = client.post(
        "/civic/cases", headers=headers,
        json={
            "case_type": "complaint",
            "subject": "Consent boundary",
            "narrative": "The case must not become ready without consent.",
            "related_office_id": "office-e2e",
        },
    )
    assert created.status_code == 200
    case_id = created.json()["case_id"]

    started = client.post(f"/civic/cases/{case_id}/review", headers=headers, json={})
    assert started.status_code == 200
    ready = client.post(f"/civic/cases/{case_id}/ready", headers=headers, json={})
    assert ready.status_code == 409
    assert "approval" in ready.json()["detail"].lower() or "consent" in ready.json()["detail"].lower()
    assert cases.get(case_id).status.value == "review"
