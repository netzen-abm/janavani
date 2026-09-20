from src.web_mvp.services.api_client import JanavaniWebAPIClient


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
