import base64
import json
import hashlib
import time
from urllib.parse import parse_qs, urlencode, urlsplit

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import rsa
from fastapi.testclient import TestClient

import src.webapp.identity_gateway as gateway
import src.webapp.oidc_client as oidc
from src.identity.http_assertion import IdentityAssertionVerifier


def _settings(monkeypatch):
    values = {
        "JANAVANI_RUNTIME_MODE": "test",
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
    for key, value in values.items():
        monkeypatch.setenv(key, value)
    return oidc.OIDCSettings.from_environment()


def test_authorization_url_uses_state_nonce_and_s256_pkce(monkeypatch):
    settings = oidc.OIDCSettings(
        "https://issuer.example", "client", "c" * 40,
        "https://webapp.example/auth/callback", "s" * 48,
        "a" * 48, "janavani-identity", "janavani-api",
    )
    monkeypatch.setattr(oidc, "load_discovery", lambda _settings: {
        "authorization_endpoint": "https://issuer.example/authorize"
    })
    transaction = oidc.new_login_transaction()
    params = parse_qs(urlsplit(oidc.authorization_url(settings, transaction)).query)
    assert params["state"] == [transaction["state"]]
    assert params["nonce"] == [transaction["nonce"]]
    assert params["code_challenge_method"] == ["S256"]
    expected = base64.urlsafe_b64encode(
        hashlib.sha256(transaction["code_verifier"].encode()).digest()
    ).rstrip(b"=").decode()
    assert params["code_challenge"] == [expected]


def test_id_token_requires_signature_issuer_audience_and_nonce(monkeypatch):
    settings = oidc.OIDCSettings(
        "https://issuer.example", "client", "c" * 40,
        "https://webapp.example/auth/callback", "s" * 48,
        "a" * 48, "janavani-identity", "janavani-api",
    )
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    jwk = json.loads(jwt.algorithms.RSAAlgorithm.to_jwk(key.public_key()))
    jwk.update({"kid": "test-key", "alg": "RS256", "use": "sig"})

    class Response:
        def raise_for_status(self):
            return None
        def json(self):
            return {"keys": [jwk]}

    monkeypatch.setattr(oidc.httpx, "get", lambda *args, **kwargs: Response())
    now = int(time.time())
    claims = {
        "iss": settings.issuer_url, "aud": settings.client_id, "sub": "stable-provider-subject",
        "iat": now, "exp": now + 180, "nonce": "nonce-value",
    }
    token = jwt.encode(claims, key, algorithm="RS256", headers={"kid": "test-key"})
    verified = oidc.verify_id_token(settings, "https://issuer.example/jwks", token, "nonce-value")
    assert verified["sub"] == "stable-provider-subject"
    with pytest.raises(oidc.OIDCAuthenticationError, match="nonce"):
        oidc.verify_id_token(settings, "https://issuer.example/jwks", token, "wrong-nonce")

    wrong_audience = dict(claims, aud="another-client")
    bad_token = jwt.encode(wrong_audience, key, algorithm="RS256", headers={"kid": "test-key"})
    with pytest.raises(oidc.OIDCAuthenticationError):
        oidc.verify_id_token(settings, "https://issuer.example/jwks", bad_token, "nonce-value")


def test_web_login_uses_encrypted_transaction_and_creates_opaque_session(monkeypatch):
    _settings(monkeypatch)
    from src.webapp.main import app

    def fake_authorization_url(settings, transaction):
        query = urlencode({
            "state": transaction["state"], "nonce": transaction["nonce"],
            "code_challenge": transaction["code_challenge"], "code_challenge_method": "S256",
        })
        return "https://issuer.example/authorize?" + query

    def fake_exchange(settings, code, transaction):
        assert code == "one-time-code"
        assert transaction["code_verifier"]
        return {"iss": settings.issuer_url, "sub": "private-provider-subject"}

    monkeypatch.setattr(gateway, "authorization_url", fake_authorization_url)
    monkeypatch.setattr(gateway, "exchange_authorization_code", fake_exchange)
    client = TestClient(app, base_url="https://webapp.example")

    started = client.get("/auth/login", follow_redirects=False)
    assert started.status_code == 303
    query = parse_qs(urlsplit(started.headers["location"]).query)
    state = query["state"][0]
    transaction_cookie = started.cookies.get("janavani_oidc_transaction")
    assert transaction_cookie and "private-provider-subject" not in transaction_cookie
    assert "HttpOnly" in started.headers["set-cookie"]
    assert "SameSite=lax" in started.headers["set-cookie"]

    callback = client.get(
        "/auth/callback?" + urlencode({"code": "one-time-code", "state": state}),
        follow_redirects=False,
    )
    assert callback.status_code == 303
    assert callback.headers["location"] == "/"
    assert "private-provider-subject" not in client.cookies.get("janavani_web_session", "")
    assert "id_token" not in client.cookies.get("janavani_web_session", "")
    home = client.get("/")
    assert "Create a Civic Case" in home.text
    assert "Sign out" in home.text

    refused = client.post("/auth/logout", follow_redirects=False)
    assert refused.status_code == 403
    logged_out = client.post("/auth/logout", headers={"Origin": "https://webapp.example"}, follow_redirects=False)
    assert logged_out.status_code == 303
    assert "Sign in securely" in client.get("/").text


def test_internal_assertion_is_short_lived_and_has_only_citizen_capabilities(monkeypatch):
    _settings(monkeypatch)
    principal = "janavani:oidc:" + "b" * 64
    assertion = gateway.api_assertion_for_session({
        "janavani_identity": {
            "principal_id": principal, "provider": "oidc", "authentication_method": "oidc"
        }
    })
    assert assertion is not None
    identity = IdentityAssertionVerifier(
        secret=("a" * 48).encode(),
        expected_issuer="janavani-identity",
        expected_audience="janavani-api",
    ).verify(assertion)
    assert identity.principal_id == principal
    assert identity.authentication_method == "oidc"
    assert "JNV-CIVIC-COMPLAINT" in identity.capabilities
    assert "administrator" not in identity.capabilities


def test_callback_rejects_state_mismatch_and_clears_transaction(monkeypatch):
    _settings(monkeypatch)
    from src.webapp.main import app
    called = []

    def fake_authorization_url(settings, transaction):
        return "https://issuer.example/authorize?" + urlencode({"state": transaction["state"]})

    def should_not_exchange(*args, **kwargs):
        called.append(True)
        raise AssertionError("Authorization code exchange must not occur after state mismatch")

    monkeypatch.setattr(gateway, "authorization_url", fake_authorization_url)
    monkeypatch.setattr(gateway, "exchange_authorization_code", should_not_exchange)
    client = TestClient(app, base_url="https://webapp.example")
    start = client.get("/auth/login", follow_redirects=False)
    assert start.status_code == 303
    response = client.get(
        "/auth/callback?" + urlencode({"code": "one-time-code", "state": "attacker-state"}),
        follow_redirects=False,
    )
    assert response.status_code == 401
    assert called == []
    assert "janavani_oidc_transaction" in response.headers.get("set-cookie", "")
    assert "Max-Age=0" in response.headers["set-cookie"]


def test_production_web_identity_rejects_insecure_issuer(monkeypatch):
    _settings(monkeypatch)
    import src.webapp.identity_gateway as web_identity
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "production")
    monkeypatch.setenv("JANAVANI_OIDC_ISSUER_URL", "http://untrusted.example")
    with pytest.raises(web_identity.OIDCConfigurationError, match="HTTPS"):
        web_identity.validate_web_identity_configuration()
