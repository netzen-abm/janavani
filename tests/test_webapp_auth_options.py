from starlette.testclient import TestClient

from src.webapp.main import app


_OIDC_KEYS = (
    "JANAVANI_OIDC_ISSUER_URL",
    "JANAVANI_OIDC_CLIENT_ID",
    "JANAVANI_OIDC_CLIENT_SECRET",
    "JANAVANI_OIDC_REDIRECT_URI",
    "JANAVANI_WEB_SESSION_SECRET",
    "JANAVANI_IDENTITY_ASSERTION_SECRET",
    "JANAVANI_IDENTITY_ASSERTION_ISSUER",
    "JANAVANI_IDENTITY_ASSERTION_AUDIENCE",
    "JANAVANI_WEB_API_URL",
)


def test_options_page_keeps_anonymous_usage_available_and_reports_unconfigured_methods(
    monkeypatch,
):
    for name in _OIDC_KEYS:
        monkeypatch.delenv(name, raising=False)

    client = TestClient(app)
    response = client.get("/auth/options")

    assert response.status_code == 200
    assert "Anonymous use is available" in response.text
    assert "Not configured in this deployment" in response.text
    assert "Email one-time-code sign-in" in response.text
    assert "SMS/mobile verification" in response.text
    assert "not available yet" in response.text
    assert response.headers["cache-control"] == "no-store, private"
    assert response.headers["content-security-policy"].startswith("default-src 'none'")
    assert client.get("/").status_code == 200


def test_options_page_exposes_web_login_only_after_oidc_settings_are_present(monkeypatch):
    values = {
        "JANAVANI_OIDC_ISSUER_URL": "https://issuer.example",
        "JANAVANI_OIDC_CLIENT_ID": "janavani-web",
        "JANAVANI_OIDC_CLIENT_SECRET": "c" * 40,
        "JANAVANI_OIDC_REDIRECT_URI": "https://webapp.example/auth/callback",
        "JANAVANI_WEB_SESSION_SECRET": "s" * 48,
        "JANAVANI_IDENTITY_ASSERTION_SECRET": "a" * 48,
        "JANAVANI_IDENTITY_ASSERTION_ISSUER": "janavani-identity",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE": "janavani-api",
        "JANAVANI_WEB_API_URL": "https://api.example",
    }
    for name, value in values.items():
        monkeypatch.setenv(name, value)

    response = TestClient(app).get("/auth/options")

    assert response.status_code == 200
    assert "Configured" in response.text
    assert "Continue to secure sign-in" in response.text
    assert "/auth/login" in response.text
    assert "private key" in response.text.lower()
