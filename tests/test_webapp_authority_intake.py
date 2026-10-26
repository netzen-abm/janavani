from fastapi.testclient import TestClient

import src.webapp.authority_intake as intake
from src.webapp.main import app


VERIFIED_AUTHORITY = {
    "authority_id": "office-verified",
    "name": "Verified District Office",
    "authority_type": "district",
    "city": "Bengaluru",
    "state": "Karnataka",
    "destination_name": "District Officer",
    "destination_address": "District Office",
    "destination_email": "office@example.test",
    "destination_role": "District Officer",
    "verified": True,
    "last_verified_at": "2026-10-20T00:00:00Z",
    "source_refs": ["test-authority-registry"],
}


class FakeWebClient:
    identity_assertion = "synthetic-test-assertion"
    base_url = "https://platform.example"

    def __init__(self, create_result=None):
        self.create_result = create_result or {"case_id": "case-synthetic", "status": "draft"}
        self.created = []

    def create_case(self, **kwargs):
        self.created.append(kwargs)
        return self.create_result


class FakeDirectory:
    def __init__(self, items):
        self.items = items
        self.calls = []

    def search(self, **kwargs):
        self.calls.append(kwargs)
        return list(self.items)


def _install_clients(monkeypatch, web_client, directory):
    monkeypatch.setattr(intake, "client_for_request", lambda request: web_client)
    monkeypatch.setattr(intake, "AuthorityDirectoryAPIClient", lambda **kwargs: directory)


def test_intake_lists_verified_authorities_without_creating_a_case(monkeypatch):
    web_client = FakeWebClient()
    directory = FakeDirectory([VERIFIED_AUTHORITY])
    _install_clients(monkeypatch, web_client, directory)
    response = TestClient(app).post(
        "/submit-issue",
        data={
            "citizen_input": "The public streetlight has been out for three nights.",
            "city": "Bengaluru",
            "authority_type": "district",
        },
    )
    assert response.status_code == 200
    assert "Choose a verified authority" in response.text
    assert "Verified District Office" in response.text
    assert 'name="authority_id"' in response.text
    assert "case-synthetic" not in response.text
    assert web_client.created == []
    assert response.headers["cache-control"] == "no-store, private"


def test_intake_revalidates_authority_before_creating_case(monkeypatch):
    web_client = FakeWebClient()
    directory = FakeDirectory([VERIFIED_AUTHORITY])
    _install_clients(monkeypatch, web_client, directory)
    response = TestClient(app).post(
        "/submit-issue/confirm",
        data={
            "citizen_input": "The public streetlight has been out for three nights.",
            "city": "Bengaluru",
            "authority_type": "district",
            "authority_id": "office-verified",
        },
    )
    assert response.status_code == 200
    assert "Case created" in response.text
    assert "case-synthetic" in response.text
    assert len(web_client.created) == 1
    assert web_client.created[0]["related_office_id"] == "office-verified"
    assert web_client.created[0]["jurisdiction"]["city"] == "Bengaluru"
    assert web_client.created[0]["subject"] == "The public streetlight has been out for three nights."
    assert len(directory.calls) == 1
    assert web_client.created[0]["narrative"] == "The public streetlight has been out for three nights."


def test_intake_rejects_tampered_or_unverified_authority_selection(monkeypatch):
    web_client = FakeWebClient()
    directory = FakeDirectory([VERIFIED_AUTHORITY])
    _install_clients(monkeypatch, web_client, directory)
    response = TestClient(app).post(
        "/submit-issue/confirm",
        data={
            "citizen_input": "Synthetic issue",
            "city": "Bengaluru",
            "authority_type": "district",
            "authority_id": "office-not-in-current-verified-results",
        },
    )
    assert response.status_code == 409
    assert "No Case was created" in response.text
    assert web_client.created == []


def test_intake_with_no_verified_authority_does_not_create_a_case(monkeypatch):
    web_client = FakeWebClient()
    directory = FakeDirectory([])
    _install_clients(monkeypatch, web_client, directory)
    response = TestClient(app).post(
        "/submit-issue",
        data={
            "citizen_input": "Synthetic issue",
            "city": "Bengaluru",
            "authority_type": "district",
        },
    )
    assert response.status_code == 200
    assert "No Case was created" in response.text
    assert web_client.created == []


def test_intake_requires_identity_before_directory_lookup(monkeypatch):
    class AnonymousClient:
        identity_assertion = None
        base_url = "https://platform.example"

    def no_lookup(**kwargs):
        raise AssertionError("Directory must not be queried before authentication")

    monkeypatch.setattr(intake, "client_for_request", lambda request: AnonymousClient())
    monkeypatch.setattr(intake, "AuthorityDirectoryAPIClient", no_lookup)
    response = TestClient(app).post(
        "/submit-issue",
        data={"citizen_input": "Synthetic issue", "city": "Bengaluru", "authority_type": "district"},
    )
    assert response.status_code == 401
    assert "Sign-in required" in response.text
