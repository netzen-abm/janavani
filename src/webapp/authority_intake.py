"""Citizen intake routes that require a verified authority before Case creation."""
from __future__ import annotations

from html import escape
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.webapp.api_errors import PlatformAPIContractError, safe_api_errors
from src.webapp.services.api_client import client_for_request
from src.webapp.services.authority_directory_client import AuthorityDirectoryAPIClient

_MAX_NARRATIVE_CHARS = 20000


def _page(title: str, body: str, *, status_code: int = 200) -> HTMLResponse:
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{escape(title)} — Janavani</title></head><body><main>'
        f'<h1>{escape(title)}</h1>{body}'
        '<p><a href="/">Return to dashboard</a></p></main></body></html>'
    )
    return HTMLResponse(document, status_code=status_code, headers={
        "Cache-Control": "no-store, private",
        "Pragma": "no-cache",
        "Referrer-Policy": "no-referrer",
        "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'none'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    })


def _clients(request: Request):
    client = client_for_request(request)
    if not client.identity_assertion:
        return client, None
    return client, AuthorityDirectoryAPIClient(
        base_url=client.base_url, identity_assertion=client.identity_assertion
    )


def _validated_inputs(citizen_input: str, city: str, authority_type: str):
    narrative = citizen_input.strip()
    city = city.strip()
    authority_type = authority_type.strip()
    if not narrative or len(narrative) > _MAX_NARRATIVE_CHARS:
        return None
    if not city or len(city) > 100 or not authority_type or len(authority_type) > 80:
        return None
    return narrative, city, authority_type


def _search_form(narrative: str, city: str, authority_type: str, items: list[dict]) -> str:
    options = []
    for item in items:
        authority_id = escape(item["authority_id"], quote=True)
        name = escape(item["name"])
        kind = escape(item["authority_type"])
        location = ", ".join(value for value in (item.get("city", ""), item.get("state", "")) if value)
        details = [escape(item.get("destination_name") or item.get("destination_role") or "Verified destination")]
        if item.get("destination_address"):
            details.append(escape(item["destination_address"]))
        if item.get("destination_email"):
            details.append(escape(item["destination_email"]))
        if location:
            details.append(escape(location))
        options.append(
            f'<label><input type="radio" name="authority_id" value="{authority_id}" required> '
            f'<strong>{name}</strong> — {kind}<br><small>{" · ".join(details)}</small></label><br>'
        )
    return (
        '<p>Choose a verified public authority. No Case has been created yet.</p>'
        '<form action="/submit-issue/confirm" method="post">'
        f'<input type="hidden" name="citizen_input" value="{escape(narrative, quote=True)}">'
        f'<input type="hidden" name="city" value="{escape(city, quote=True)}">'
        f'<input type="hidden" name="authority_type" value="{escape(authority_type, quote=True)}">'
        + "".join(options)
        + '<p><button type="submit">Create Case with selected authority</button></p></form>'
    )


def register_authority_intake_routes(rt) -> None:
    """Register the two-step search/select/create citizen workflow."""

    @rt("/submit-issue", methods=["POST"])
    @safe_api_errors("search verified authorities")
    def post_submit_issue(
        request: Request, citizen_input: str = "", city: str = "", authority_type: str = ""
    ):
        client, directory = _clients(request)
        if directory is None:
            return _page("Sign-in required", "<p>Authenticate through Janavani before creating a Case.</p>", status_code=401)
        validated = _validated_inputs(citizen_input, city, authority_type)
        if validated is None:
            return _page("More information required", "<p>Provide an issue description, city, and authority type. No Case was created.</p>", status_code=422)
        narrative, city, authority_type = validated
        items = directory.search(authority_type=authority_type, city=city, limit=10)
        if not items:
            return _page("No verified authority found", (
                f"<p>No verified {escape(authority_type)} destination was found for {escape(city)}. "
                "No Case was created. Check the location/type or try again later.</p>"
            ))
        return _page("Choose a verified authority", _search_form(narrative, city, authority_type, items))

    @rt("/submit-issue/confirm", methods=["POST"])
    @safe_api_errors("create a Case for the selected authority")
    def post_confirm_authority(
        request: Request, citizen_input: str = "", city: str = "",
        authority_type: str = "", authority_id: str = ""
    ):
        client, directory = _clients(request)
        if directory is None:
            return _page("Sign-in required", "<p>Authenticate through Janavani before creating a Case.</p>", status_code=401)
        validated = _validated_inputs(citizen_input, city, authority_type)
        if validated is None or not authority_id.strip():
            return _page("Selection invalid", "<p>Provide the issue details and choose a verified authority. No Case was created.</p>", status_code=422)
        narrative, city, authority_type = validated
        items = directory.search(authority_type=authority_type, city=city, limit=10)
        selected = next((item for item in items if item["authority_id"] == authority_id), None)
        if selected is None:
            return _page("Authority selection expired", (
                "<p>This destination is no longer verified or no longer matches the search. "
                "No Case was created. Search again and choose a current verified destination.</p>"
            ), status_code=409)
        subject = " ".join(narrative.splitlines()[0].split())[:120] or "Citizen civic issue"
        result = client.create_case(
            subject=subject, narrative=narrative, case_type="complaint",
            related_office_id=authority_id,
            jurisdiction={"city": city, "authority_name": selected["name"]},
        )
        if not isinstance(result, dict):
            raise PlatformAPIContractError("Platform API returned an invalid Case result")
        case_id, status = result.get("case_id"), result.get("status")
        if not isinstance(case_id, str) or not case_id.strip() or not isinstance(status, str) or not status.strip():
            raise PlatformAPIContractError("Platform API returned an incomplete Case result")
        safe_case_id = escape(case_id, quote=True)
        return _page("Case created", (
            f"<p>Case ID: {escape(case_id)}</p><p>Status: {escape(status)}</p>"
            "<p>The Case is linked to the selected verified authority. Review the generated document before using it.</p>"
            f'<p><a href="/cases/{safe_case_id}/prepare">Open Case workspace</a></p>'
        ))
