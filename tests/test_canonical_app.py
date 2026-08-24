"""M3-D.4 canonical FastAPI assembly verification."""

from fastapi.testclient import TestClient

from src.web.canonical_app import app


def test_canonical_app_imports() -> None:
    assert app is not None
    assert app.title == "Janavani Platform API"


def test_canonical_platform_endpoints() -> None:
    client = TestClient(app)

    assert client.get("/liveness").status_code == 200
    assert client.get("/liveness").json() == {"status": "alive"}

    response = client.get("/version")
    assert response.status_code == 200
    assert response.json() == {
        "service": "janavani-platform-api",
        "version": "canonical-m3",
    }


def test_canonical_domain_route_prefixes() -> None:
    """Verify published canonical API paths through FastAPI's OpenAPI surface."""
    client = TestClient(app)
    paths = set(client.get("/openapi.json").json()["paths"])

    assert "/api/v1/feedback/submit" in paths
    assert "/api/v1/feedback/summary/{office_id}" in paths
    assert "/api/v1/legislative/directory/{constituency_code}" in paths
    assert "/api/v1/legislative/dispatch-email" in paths
    assert "/api/v1/constitutional/bill/{bill_code}" in paths
    assert "/api/v1/constitutional/generate-objection" in paths
    assert "/api/v1/land/compile-kml" in paths


def test_legacy_app_is_not_imported_by_canonical_assembly() -> None:
    import sys

    assert "src.web.app" not in sys.modules
