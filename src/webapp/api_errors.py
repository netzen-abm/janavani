"""Safe, truthful presentation of failures from the canonical Platform API.

This boundary maps transport/API failures to user-facing status pages without
leaking response bodies, identity assertions, internal URLs, or stack details.
It preserves domain ownership in the API and never reports uncertain writes as
successful.
"""
from __future__ import annotations

from functools import wraps
from html import escape
from typing import Callable

import httpx
from starlette.responses import HTMLResponse


def api_failure_response(exc: Exception, *, action: str) -> HTMLResponse:
    """Return a no-store response with a stable status and no internal details."""
    status_code = 503
    title = "Request temporarily unavailable"
    message = (
        f"Janavani could not confirm the result of this request. "
        f"Reopen your Case to check its current state before retrying."
    )

    if isinstance(exc, httpx.HTTPStatusError):
        remote_status = exc.response.status_code
        if remote_status in (401, 403):
            status_code = 403
            title = "Access unavailable"
            message = (
                "Your sign-in may have expired, or this Case is not available "
                "to this account."
            )
        elif remote_status == 404:
            status_code = 404
            title = "Case or document unavailable"
            message = "The requested Case or document is not available to this account."
        elif remote_status == 409:
            status_code = 409
            title = "Case state changed"
            message = "Reopen the Case and review its current state before continuing."
        elif remote_status in (400, 422):
            status_code = 422
            title = "Request not accepted"
            message = "The request was not accepted. Review the details and try again."
    elif isinstance(exc, ValueError):
        status_code = 422
        title = "Request not accepted"
        message = "The requested details could not be processed. Review them and try again."

    # action is a source-defined constant supplied by a route, never user input.
    safe_action = escape(action)
    body = (
        "<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
        f"<title>{escape(title)} — Janavani</title></head><body><main>"
        f"<h1>{escape(title)}</h1><p>{message}</p>"
        f"<p>Requested action: {safe_action}.</p>"
        "<p><a href=\"/cases\">Return to Cases</a></p>"
        "</main></body></html>"
    )
    return HTMLResponse(
        body,
        status_code=status_code,
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": (
                "default-src 'none'; base-uri 'none'; form-action 'none'; "
                "frame-ancestors 'none'"
            ),
        },
    )


def safe_api_errors(action: str):
    """Convert expected API/transport failures into truthful, non-leaking UI errors."""
    def decorate(handler: Callable):
        @wraps(handler)
        def wrapped(*args, **kwargs):
            try:
                return handler(*args, **kwargs)
            except (httpx.HTTPError, RuntimeError, ValueError) as exc:
                return api_failure_response(exc, action=action)
        return wrapped
    return decorate
