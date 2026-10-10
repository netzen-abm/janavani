from src.webapp.services.api_client import JanavaniWebAPIClient


def test_web_client_requires_verified_identity_assertion():
    client = JanavaniWebAPIClient(base_url="http://example.invalid", identity_assertion=None)
    try:
        client._headers()
    except RuntimeError as exc:
        assert "identity" in str(exc).lower()
    else:
        raise AssertionError("Web adapter must fail closed without authenticated identity")


def test_web_client_never_constructs_actor_identity_from_request_data():
    client = JanavaniWebAPIClient(
        base_url="http://example.invalid",
        identity_assertion="verified-assertion",
    )
    assert client._headers() == {"Authorization": "Bearer verified-assertion"}


def test_web_client_ignores_process_wide_identity_assertion(monkeypatch):
    monkeypatch.setenv("JANAVANI_WEB_IDENTITY_ASSERTION", "shared-citizen-identity")
    client = JanavaniWebAPIClient(base_url="http://example.invalid")
    try:
        client._headers()
    except RuntimeError:
        pass
    else:
        raise AssertionError("A process-wide identity assertion must never authenticate web citizens")


def test_web_client_uses_only_request_scoped_gateway_cookie():
    from types import SimpleNamespace
    from src.webapp.services.api_client import client_for_request

    request = SimpleNamespace(cookies={"janavani_identity_assertion": "per-user-signed-assertion"})
    assert client_for_request(request)._headers() == {
        "Authorization": "Bearer per-user-signed-assertion"
    }


def test_web_client_fails_closed_without_gateway_cookie():
    from types import SimpleNamespace
    from src.webapp.services.api_client import client_for_request

    client = client_for_request(SimpleNamespace(cookies={}))
    try:
        client._headers()
    except RuntimeError as exc:
        assert "identity" in str(exc).lower()
    else:
        raise AssertionError("Missing gateway assertion must fail closed")
