"""Same-origin protection for cookie-authenticated WebApp mutations."""
from __future__ import annotations

from urllib.parse import urlsplit

from starlette.datastructures import Headers
from starlette.requests import Request
from starlette.responses import JSONResponse


_MUTATING_METHODS = frozenset({"POST", "PUT", "PATCH", "DELETE"})
_IDENTITY_COOKIE = "janavani_identity_assertion"


def _same_origin(source: str | None, host: str | None) -> bool:
    """Compare source and request host, normalizing default HTTP(S) ports."""
    if not source or not host:
        return False
    try:
        source_url = urlsplit(source)
        request_host = urlsplit("//" + host)
        if source_url.scheme not in {"http", "https"} or not source_url.hostname or not request_host.hostname:
            return False
        if source_url.hostname.lower() != request_host.hostname.lower():
            return False
        default_port = 443 if source_url.scheme == "https" else 80
        source_port = source_url.port or default_port
        request_port = request_host.port or default_port
        return source_port == request_port
    except ValueError:
        return False


class SameOriginCookieMutationMiddleware:
    """Reject cross-origin unsafe methods when the request carries citizen auth.

    API bearer verification remains authoritative. This middleware protects the
    WebApp's browser trust boundary where an HttpOnly identity cookie is read
    server-side and forwarded as an Authorization header.
    """

    def __init__(self, app, cookie_name: str = _IDENTITY_COOKIE) -> None:
        self.app = app
        self.cookie_name = cookie_name

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http" or scope.get("method", "GET").upper() not in _MUTATING_METHODS:
            await self.app(scope, receive, send)
            return

        request = Request(scope)
        if not request.cookies.get(self.cookie_name):
            await self.app(scope, receive, send)
            return

        headers = Headers(scope=scope)
        # A supplied Origin is authoritative; do not fall back to a friendly
        # Referer when Origin is present but invalid.
        source = headers.get("origin") if headers.get("origin") is not None else headers.get("referer")
        if not _same_origin(source, headers.get("host")):
            response = JSONResponse(
                {"detail": "Cross-origin browser mutation rejected"},
                status_code=403,
                headers={"Cache-Control": "no-store"},
            )
            await response(scope, receive, send)
            return

        await self.app(scope, receive, send)
