from fastapi.testclient import TestClient

from src.web.canonical_app import app
from src.web.civic_case_router import _CASES


client = TestClient(app)


def setup_function() -> None:
    _CASES.clear()


def test_case_api_preserves_review_and_delivery_truth() -> None:
    create = client.post(
        "/civic/cases",
        json={
            "case_id": "case-api-1",
            "case_type": "complaint",
            "subject": "Delayed public service",
            "narrative": "The requested service has not been delivered.",
        },
    )
    assert create.status_code == 200
    assert create.json()["status"] == "draft"

    review = client.post(
        "/civic/cases/case-api-1/review",
        json={"event_id": "e1", "occurred_at": "2026-08-24T00:00:00Z"},
    )
    assert review.status_code == 200
    assert review.json()["status"] == "review"

    consent = client.post(
        "/civic/cases/case-api-1/consent",
        json={"consent_id": "consent-1"},
    )
    assert consent.status_code == 200

    ready = client.post(
        "/civic/cases/case-api-1/ready",
        json={"event_id": "e2", "occurred_at": "2026-08-24T00:01:00Z"},
    )
    assert ready.status_code == 200
    assert ready.json()["status"] == "ready"

    submitting = client.post(
        "/civic/cases/case-api-1/submitting",
        json={"event_id": "e3", "occurred_at": "2026-08-24T00:02:00Z"},
    )
    assert submitting.json()["status"] == "submitting"

    submitted = client.post(
        "/civic/cases/case-api-1/submit",
        json={"event_id": "e4", "occurred_at": "2026-08-24T00:03:00Z"},
    )
    assert submitted.json()["status"] == "submitted"

    acknowledged = client.post(
        "/civic/cases/case-api-1/acknowledge",
        json={
            "event_id": "e5",
            "occurred_at": "2026-08-24T00:04:00Z",
            "source_channel": "web",
            "notes": "ACK-1",
        },
    )
    assert acknowledged.json()["status"] == "acknowledged"

    fetched = client.get("/civic/cases/case-api-1")
    assert fetched.status_code == 200
    assert fetched.json()["status"] == "acknowledged"
    assert len(fetched.json()["events"]) == 5
