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


def test_user_controlled_action_label_is_html_escaped():
    response = api_failure_response(RuntimeError("private details"), action="<script>secret()</script>")
    body = response.body.decode()

    assert "<script>" not in body
    assert "&lt;script&gt;" in body
