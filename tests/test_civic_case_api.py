import base64
import hashlib
import hmac
import json
import time

from fastapi.testclient import TestClient

from src.web.canonical_app import app
from src.web.civic_case_router import _REPOSITORY


SECRET = "test-identity-secret"
client = TestClient(app)


def setup_function() -> None:
    if hasattr(_REPOSITORY, "clear"):
        _REPOSITORY.clear()
    import os
    os.environ["JANAVANI_IDENTITY_ASSERTION_SECRET"] = SECRET


def _auth_header(principal_id: str = "principal-1") -> dict[str, str]:
    now = int(time.time())
    payload = {
        "iss": "janavani-identity", "aud": "janavani-api", "sub": principal_id,
        "provider": "test-identity", "subject": principal_id, "principal_id": principal_id,
        "authentication_method": "passkey", "iat": now, "exp": now + 60,
        "jti": f"test-{principal_id}-{now}",
        "capabilities": ["case:read", "case:write", "case:review", "case:evidence", "case:submit"],
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    signature = hmac.new(SECRET.encode("utf-8"), encoded.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return {"Authorization": f"Bearer {encoded}.{signed}"}


def test_case_api_enforces_authenticated_ownership_and_preserves_delivery_truth() -> None:
    unauthenticated = client.post(
        "/civic/cases", json={"case_type": "corruption", "subject": "x", "narrative": "x"}
    )
    assert unauthenticated.status_code == 401

    create = client.post(
        "/civic/cases", headers=_auth_header("principal-1"),
        json={"case_id": "legacy-client-id-ignored", "case_type": "corruption",
              "subject": "Delayed public service", "narrative": "The requested service has not been delivered.",
              "created_by": "attacker-supplied-id", "jurisdiction": {"district": "Bengaluru Urban"},
              "related_organisation_id": "org-1", "related_office_id": "office-1",
              "related_official_id": "official-1", "related_representative_id": "rep-1",
              "claims": [{"claim_id": "claim-1", "statement": "Service delayed"}]},
    )
    assert create.status_code == 200
    case_id = create.json()["case_id"]
    assert case_id.startswith("case-") and case_id != "legacy-client-id-ignored"
    assert create.json()["status"] == "draft"

    assert client.get(f"/civic/cases/{case_id}", headers=_auth_header("principal-2")).status_code == 404
    review = client.post(f"/civic/cases/{case_id}/review", headers=_auth_header(), json={})
    assert review.status_code == 200 and review.json()["status"] == "review"
    consent = client.post(f"/civic/cases/{case_id}/consent", headers=_auth_header(), json={"consent_id": "consent-1"})
    assert consent.status_code == 200
    ready = client.post(f"/civic/cases/{case_id}/ready", headers=_auth_header(), json={})
    assert ready.status_code == 200 and ready.json()["status"] == "ready"
    submitting = client.post(f"/civic/cases/{case_id}/submitting", headers=_auth_header(), json={})
    assert submitting.status_code == 200 and submitting.json()["status"] == "submitting"
    queued = client.post(f"/civic/cases/{case_id}/queued", headers=_auth_header(), json={})
    assert queued.status_code == 200 and queued.json()["status"] == "queued"
    submitted = client.post(f"/civic/cases/{case_id}/submit", headers=_auth_header(), json={})
    assert submitted.status_code == 409

    fetched = client.get(f"/civic/cases/{case_id}", headers=_auth_header())
    assert fetched.status_code == 200
    body = fetched.json()
    assert body["created_by"] == "principal-1"
    assert body["status"] == "queued"
    assert body["jurisdiction"]["district"] == "Bengaluru Urban"
    assert body["related_organisation_id"] == "org-1"
    assert body["related_official_id"] == "official-1"
    assert body["related_representative_id"] == "rep-1"
    assert body["claims"][0]["claim_id"] == "claim-1"
    assert len(body["events"]) == 5
