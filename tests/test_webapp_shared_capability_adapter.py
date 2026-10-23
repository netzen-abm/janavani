import pytest

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


def test_lifecycle_requests_forward_transient_citizen_content(monkeypatch):
    import src.webapp.services.api_client as api_module

    calls = []

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"status": "review"}

    def fake_post(url, *, json, headers, timeout):
        calls.append({"url": url, "json": json, "headers": headers, "timeout": timeout})
        return Response()

    monkeypatch.setattr(api_module.httpx, "post", fake_post)
    client = JanavaniWebAPIClient(
        base_url="https://api.example.test",
        identity_assertion="signed-user-assertion",
    )
    client.start_review("case-123", subject="Water outage", narrative="Supply stopped.")
    client.mark_ready("case-123", subject="Water outage", narrative="Supply stopped.")

    assert calls[0]["json"] == {
        "subject": "Water outage", "narrative": "Supply stopped."
    }
    assert calls[1]["json"] == {
        "subject": "Water outage", "narrative": "Supply stopped."
    }
    assert all(
        call["headers"] == {"Authorization": "Bearer signed-user-assertion"}
        for call in calls
    )



def test_web_client_lists_owned_case_metadata_with_request_scoped_identity(monkeypatch):
    import src.webapp.services.api_client as api_module

    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"items": [{"case_id": "case-owned-1", "status": "review"}], "count": 1}

    def fake_get(url, *, params, headers, timeout):
        captured.update(url=url, params=params, headers=headers, timeout=timeout)
        return Response()

    monkeypatch.setattr(api_module.httpx, "get", fake_get)
    client = JanavaniWebAPIClient(
        base_url="https://api.example.test",
        identity_assertion="signed-citizen-assertion",
    )
    items = client.list_cases(limit=100)

    assert items == [{"case_id": "case-owned-1", "status": "review"}]
    assert captured["url"] == "https://api.example.test/civic/cases"
    assert captured["params"] == {"limit": 50}
    assert captured["headers"] == {"Authorization": "Bearer signed-citizen-assertion"}



def test_case_api_paths_encode_untrusted_ids_and_keep_endpoint_boundaries():
    client = JanavaniWebAPIClient(
        base_url="https://api.example.test",
        identity_assertion="signed-citizen-assertion",
    )

    assert client._case_url("case-123") == "https://api.example.test/civic/cases/case-123"
    assert client._case_url("case ?#id", "/document/draft") == (
        "https://api.example.test/civic/cases/case%20%3F%23id/document/draft"
    )

    for invalid_case_id in ("", ".", "..", "nested/id", r"nested\\id"):
        with pytest.raises(ValueError, match="Invalid Case ID"):
            client._case_url(invalid_case_id)
