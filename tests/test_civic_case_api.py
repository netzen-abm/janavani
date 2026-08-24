from fastapi.testclient import TestClient

from src.web.canonical_app import app


client = TestClient(app)
POLICY = "case-private"


def test_civic_case_requires_access_policy_header():
    response = client.post(
        "/civic/cases",
        json={
            "case_id": "api-case-1",
            "case_type": "complaint",
            "subject": "Road",
            "narrative": "Broken road",
        },
    )
    assert response.status_code == 400


def test_civic_case_create_get_and_wrong_policy_are_enforced():
    response = client.post(
        "/civic/cases",
        headers={"X-Access-Policy-Ref": POLICY},
        json={
            "case_id": "api-case-2",
            "case_type": "complaint",
            "subject": "Road",
            "narrative": "Broken road",
        },
    )
    assert response.status_code == 200

    response = client.get("/civic/cases/api-case-2", headers={"X-Access-Policy-Ref": POLICY})
    assert response.status_code == 200
    assert response.json()["status"] == "draft"

    response = client.get("/civic/cases/api-case-2", headers={"X-Access-Policy-Ref": "other-policy"})
    assert response.status_code == 403


def test_civic_case_requires_consent_before_ready():
    response = client.post(
        "/civic/cases",
        headers={"X-Access-Policy-Ref": POLICY},
        json={
            "case_id": "api-case-3",
            "case_type": "complaint",
            "subject": "Road",
            "narrative": "Broken road",
        },
    )
    assert response.status_code == 200

    response = client.post("/civic/cases/api-case-3/ready", headers={"X-Access-Policy-Ref": POLICY})
    assert response.status_code == 422

    response = client.post(
        "/civic/cases/api-case-3/consent",
        headers={"X-Access-Policy-Ref": POLICY},
        json={"consent_id": "consent-3"},
    )
    assert response.status_code == 200

    response = client.post("/civic/cases/api-case-3/ready", headers={"X-Access-Policy-Ref": POLICY})
    assert response.status_code == 200
    assert response.json()["status"] == "ready"

    response = client.post("/civic/cases/api-case-3/submit", headers={"X-Access-Policy-Ref": POLICY})
    assert response.status_code == 200
    assert response.json()["status"] == "submitted"
    assert response.json()["acknowledged"] is False
