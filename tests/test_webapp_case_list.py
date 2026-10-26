from types import SimpleNamespace

from fastapi.testclient import TestClient


def test_case_list_requires_request_scoped_identity(monkeypatch):
    import src.webapp.case_list as case_list
    from src.webapp.main import app

    monkeypatch.setattr(
        case_list, "client_for_request",
        lambda request: SimpleNamespace(identity_assertion=None),
    )
    response = TestClient(app).get("/cases")

    assert response.status_code == 200
    assert "Sign-in required" in response.text


def test_case_list_renders_metadata_without_private_narrative(monkeypatch):
    import src.webapp.case_list as case_list
    from src.webapp.main import app

    class Client:
        identity_assertion = "signed-citizen-assertion"

        def list_cases(self, *, limit):
            assert limit == 20
            return [{
                "case_id": "case-owned-1",
                "case_type": "complaint",
                "status": "review",
                "evidence_count": 2,
                "document_count": 1,
                "narrative": "private citizen narrative must remain hidden",
            }]

    monkeypatch.setattr(case_list, "client_for_request", lambda request: Client())
    response = TestClient(app).get("/cases")

    assert response.status_code == 200
    assert "case-owned-1" in response.text
    assert "review" in response.text
    assert "Evidence: 2" in response.text
    assert "Documents: 1" in response.text
    assert "private citizen narrative must remain hidden" not in response.text
