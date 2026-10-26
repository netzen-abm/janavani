import httpx

from src.webapp.api_errors import api_failure_response, safe_api_errors


def _status_error(status_code: int, detail: str) -> httpx.HTTPStatusError:
    request = httpx.Request("GET", "https://internal.example/private-case")
    response = httpx.Response(
        status_code,
        request=request,
        text=detail,
        headers={"content-type": "text/plain"},
    )
    return httpx.HTTPStatusError(
        f"upstream detail must not escape: {detail}",
        request=request,
        response=response,
    )


def test_api_failure_redacts_upstream_body_and_identity_like_strings():
    response = api_failure_response(
        _status_error(403, "principal=private-citizen-secret bearer=do-not-render"),
        action="open the Case workspace",
    )

    assert response.status_code == 403
    assert "Access unavailable" in response.body.decode()
    assert "private-citizen-secret" not in response.body.decode()
    assert "do-not-render" not in response.body.decode()
    assert "internal.example" not in response.body.decode()
    assert response.headers["cache-control"] == "no-store, private"
    assert response.headers["referrer-policy"] == "no-referrer"
    assert response.headers["x-content-type-options"] == "nosniff"


def test_api_failure_maps_missing_case_without_disclosing_upstream_details():
    response = api_failure_response(
        _status_error(404, "database row 22, private narrative"),
        action="open the Case workspace",
    )

    assert response.status_code == 404
    assert "Case or document unavailable" in response.body.decode()
    assert "database row 22" not in response.body.decode()
    assert "private narrative" not in response.body.decode()


def test_api_failure_treats_transport_error_as_unknown_result():
    request = httpx.Request("POST", "https://internal.example/civic/cases")
    error = httpx.ConnectError("connection to private-host failed with token=secret", request=request)

    response = api_failure_response(error, action="create a Case")
    body = response.body.decode()

    assert response.status_code == 503
    assert "could not confirm the result" in body
    assert "private-host" not in body
    assert "token=secret" not in body
    assert response.headers["cache-control"] == "no-store, private"


def test_safe_api_errors_converts_expected_failures_without_swallowing_programming_errors():
    @safe_api_errors("save the reviewed document")
    def save_document():
        raise _status_error(409, "private concurrency details")

    response = save_document()

    assert response.status_code == 409
    assert "Case state changed" in response.body.decode()
    assert "private concurrency details" not in response.body.decode()

    @safe_api_errors("read Case")
    def broken_handler():
        raise KeyError("bug should remain visible to the test harness")

    try:
        broken_handler()
    except KeyError as exc:
        assert "bug should remain visible" in str(exc)
    else:
        raise AssertionError("Unexpected programming errors must not be hidden")

    @safe_api_errors("read Case")
    def runtime_bug():
        raise RuntimeError("unexpected programming defect")

    try:
        runtime_bug()
    except RuntimeError as exc:
        assert "unexpected programming defect" in str(exc)
    else:
        raise AssertionError("Unexpected runtime defects must remain visible")


def test_user_controlled_action_label_is_html_escaped():
    response = api_failure_response(RuntimeError("private details"), action="<script>secret()</script>")
    body = response.body.decode()

    assert "<script>" not in body
    assert "&lt;script&gt;" in body

def test_case_intake_does_not_leak_authority_lookup_transport_errors(monkeypatch):
    from fastapi.testclient import TestClient
    import src.webapp.authority_intake as intake
    from src.webapp.main import app

    class Client:
        identity_assertion = "synthetic-test-assertion"
        base_url = "https://internal.example"

    class Directory:
        def __init__(self, **kwargs):
            pass

        def search(self, **kwargs):
            request = httpx.Request("GET", "https://internal.example/civic/authorities/search")
            raise httpx.ConnectError("internal host and bearer=synthetic-secret", request=request)

    monkeypatch.setattr(intake, "client_for_request", lambda request: Client())
    monkeypatch.setattr(intake, "AuthorityDirectoryAPIClient", Directory)
    response = TestClient(app).post(
        "/submit-issue",
        data={
            "citizen_input": "Synthetic streetlight issue",
            "city": "Bengaluru",
            "authority_type": "district",
        },
    )

    assert response.status_code == 503
    assert "could not confirm the result" in response.text
    assert "internal.example" not in response.text
    assert "synthetic-secret" not in response.text
    assert "Case created" not in response.text
    assert response.headers["cache-control"] == "no-store, private"


def test_case_intake_never_treats_api_error_payload_as_case_creation(monkeypatch):
    from fastapi.testclient import TestClient
    import src.webapp.authority_intake as intake
    from src.webapp.main import app

    class Client:
        identity_assertion = "synthetic-test-assertion"
        base_url = "https://internal.example"

        def create_case(self, **kwargs):
            return {"error": "private upstream database details"}

    class Directory:
        def __init__(self, **kwargs):
            pass

        def search(self, **kwargs):
            return [{
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
            }]

    monkeypatch.setattr(intake, "client_for_request", lambda request: Client())
    monkeypatch.setattr(intake, "AuthorityDirectoryAPIClient", Directory)
    response = TestClient(app).post(
        "/submit-issue/confirm",
        data={
            "citizen_input": "Synthetic streetlight issue",
            "city": "Bengaluru",
            "authority_type": "district",
            "authority_id": "office-verified",
        },
    )

    assert response.status_code == 503
    assert "Case created" not in response.text
    assert "private upstream database details" not in response.text
