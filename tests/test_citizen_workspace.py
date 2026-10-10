from pathlib import Path

from fastapi.testclient import TestClient

from src.web.canonical_app import create_canonical_app


def test_citizen_workspace_is_served_without_third_party_dependencies(monkeypatch):
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "development")
    monkeypatch.setenv("JANAVANI_IDENTITY_ASSERTION_SECRET", "test-only-secret")
    client = TestClient(create_canonical_app())

    page = client.get("/app")
    script = client.get("/app.js")
    root = client.get("/")

    assert page.status_code == 200
    assert "text/html" in page.headers["content-type"]
    assert page.headers["cache-control"] == "no-store"
    assert "connect-src 'none'" in page.headers["content-security-policy"]
    assert page.headers["permissions-policy"] == "camera=(), microphone=(), geolocation=()"
    assert page.headers["x-frame-options"] == "DENY"
    assert "Janavani Citizen Workspace" in page.text
    assert "does not send your details" in page.text
    assert 'src="/app.js"' in page.text

    assert script.status_code == 200
    assert "text/javascript" in script.headers["content-type"]
    assert script.headers["cache-control"] == "no-store"
    assert "URL.createObjectURL" in script.text
    assert "window.print()" in script.text
    assert "fetch(" not in script.text
    assert "XMLHttpRequest" not in script.text

    assert root.status_code == 200
    assert root.json()["citizen_workspace"] == "/app"
