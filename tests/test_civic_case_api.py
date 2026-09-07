import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient

from src.web.canonical_app import app
from src.web.civic_case_router import _CASES


SECRET = "test-identity-secret"
client = TestClient(app)


def setup_function() -> None:
    _CASES.clear()
    import os

    os.environ["JANAVANI_IDENTITY_ASSERTION_SECRET"] = SECRET


def _auth_header(principal_id: str = "principal-1") -> dict[str, str]:
    now = int(time.time())
    payload = {
        "iss": "janavani-identity",
        "aud": "janavani-api",
        "sub": principal_id,
        "provider": "test-identity",
        "subject": principal_id,
        "principal_id": principal_id,
        "authentication_method": "passkey",
        "iat": now,
        "exp": now + 60,
        "jti": f"test-{principal_id}-{now}",
        "capabilities": [
            "case:read",
            "case:write",
            "case:review",
            "case:evidence",
            "case:submit",
        ],
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    signature = hmac.new(SECRET.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return {"Authorization": f"Bearer {encoded}.{signed}"}


def test_case_api_enforces_authenticated_ownership_and_preserves_delivery_truth() -> None:
    unauthenticated = client.post(
        "/civic/cases",
        json={"case_id": "case-unauth", "case_type": "corruption", "subject": "x", "narrative": "x"},
    )
    assert unauthenticated.status_code == 401

    create = client.post(
        "/civic/cases",
        headers=_auth_header("principal-1"),
        json={
            "case_id": "case-api-1",
            "case_type": "corruption",
            "subject": "Delayed public service",
            "narrative": "The requested service has not been delivered.",
            "created_by": "attacker-supplied-id",
            "jurisdiction": {"district": "Bengaluru Urban"},
            "related_organisation_id": "org-1",
            "related_office_id": "office-1",
            "related_official_id": "official-1",
            "related_representative_id": "rep-1",
            "claims": [{"claim_id": "claim-1", "statement": "Service delayed"}],
        },
    )
    assert create.status_code == 200
    assert create.json()["status"] == "draft"

    forbidden_owner = client.get("/civic/cases/case-api-1", headers=_auth_header("principal-2"))
    assert forbidden_owner.status_code == 404

    review = client.post(
        "/civic/cases/case-api-1/review",
        headers=_auth_header(),
        json={"event_id": "e1", "occurred_at": "2026-08-24T00:00:00Z"},
    )
    assert review.status_code == 200
    assert review.json()["status"] == "review"

    consent = client.post(
        "/civic/cases/case-api-1/consent",
        headers=_auth_header(),
        json={"consent_id": "consent-1"},
    )
    assert consent.status_code == 200

    ready = client.post(
        "/civic/cases/case-api-1/ready",
        headers=_auth_header(),
        json={"event_id": "e2", "occurred_at": "2026-08-24T00:01:00Z"},
    )
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"

    submitting = client.post(
        "/civic/cases/case-api-1/submitting",
        headers=_auth_header(),
        json={"event_id": "e3", "occurred_at": "2026-08-24T00:02:00Z"},
    )
    assert submitting.status_code == 200
    assert submitting.json()["status"] == "submitting"

    queued = client.post(
        "/civic/cases/case-api-1/queued",
        headers=_auth_header(),
        json={"event_id": "e4", "occurred_at": "2026-08-24T00:03:00Z"},
    )
    assert queued.status_code == 200
    assert queued.json()["status"] == "queued"

    # External submission is consequential. The shared authorization kernel must
    # refuse it until the future explicit-approval capability is implemented.
    submitted = client.post(
        "/civic/cases/case-api-1/submit",
        headers=_auth_header(),
        json={"event_id": "e5", "occurred_at": "2026-08-24T00:04:00Z"},
    )
    assert submitted.status_code == 409

    fetched = client.get("/civic/cases/case-api-1", headers=_auth_header())
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["created_by"] == "principal-1"
    assert body["status"] == "queued"
    assert body["jurisdiction"]["district"] == "Bengaluru Urban"
    assert body["related_organisation_id"] == "org-1"
    assert body["related_official_id"] == "official-1"
    assert body["related_representative_id"] == "rep-1"
    assert body["claims"][0]["claim_id"] == "claim-1"
    assert len(body["events"]) == 4
