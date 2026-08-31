from fastapi.testclient import TestClient

from src.web.canonical_app import create_canonical_app


def test_create_and_get_case() -> None:
    client = TestClient(create_canonical_app())
    response = client.post("/civic/cases", json={"issue": "Broken streetlight"})
    assert response.status_code == 201
    case = response.json()
    assert case["issue"] == "Broken streetlight"

    fetched = client.get(f"/civic/cases/{case['case_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["case_id"] == case["case_id"]


def test_get_missing_case_returns_404() -> None:
    client = TestClient(create_canonical_app())
    response = client.get("/civic/cases/does-not-exist")
    assert response.status_code == 404


def test_submission_requires_workflow_prerequisites() -> None:
    client = TestClient(create_canonical_app())
    created = client.post("/civic/cases", json={"issue": "Service delay"}).json()
    response = client.post(
        f"/civic/cases/{created['case_id']}/submission",
        json={"destination_ref": "AUTH-1"},
    )
    assert response.status_code == 409


def test_submission_cannot_be_read_under_another_case() -> None:
    client = TestClient(create_canonical_app())
    first = client.post("/civic/cases", json={"issue": "First"}).json()
    second = client.post("/civic/cases", json={"issue": "Second"}).json()
    response = client.get(
        f"/civic/cases/{second['case_id']}/submission/not-owned-by-case"
    )
    assert response.status_code == 404
    assert first["case_id"] != second["case_id"]
