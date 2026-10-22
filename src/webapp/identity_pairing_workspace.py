"""Cookie-authenticated Web UI for explicit Web↔Telegram pairing."""
from __future__ import annotations

from html import escape
from urllib.parse import quote

import httpx
from starlette.requests import Request
from starlette.responses import HTMLResponse

from src.webapp.services.api_client import client_for_request
from src.webapp.services.identity_pairing_client import IdentityPairingAPIClient


def _page(title: str, body: str, *, status_code: int = 200) -> HTMLResponse:
    """Return non-cacheable, script-free HTML for the sensitive pairing flow."""
    safe_title = escape(title)
    document = (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width, initial-scale=1">'
        f'<title>{safe_title} — Janavani</title></head><body><main>'
        f'<h1>{safe_title}</h1>{body}<p><a href="/">Return to dashboard</a></p>'
        '</main></body></html>'
    )
    return HTMLResponse(
        document,
        status_code=status_code,
        headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; style-src 'unsafe-inline'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
        },
    )


def _api_client(request: Request) -> tuple[object, IdentityPairingAPIClient | None]:
    web_client = client_for_request(request)
    if not web_client.identity_assertion:
        return web_client, None
    return web_client, IdentityPairingAPIClient(
        base_url=web_client.base_url,
        identity_assertion=web_client.identity_assertion,
    )


def _sign_in_required() -> HTMLResponse:
    return _page(
        "Sign-in required",
        '<p>Your Janavani identity session is missing or expired. Sign in again before linking Telegram.</p>',
    )


def _confirm_form(pairing_id: str, *, note: str = "") -> str:
    action = escape(f"/identity/telegram/pair/{quote(pairing_id, safe='')}/confirm", quote=True)
    return (
        f"{note}<form action=\"{action}\" method=\"post\">"
        '<label><input type="checkbox" name="explicit_confirmation" value="yes" required> '
        "I confirm that I initiated this pairing and want to link this Telegram account to my Janavani account."
        '</label><p><button type="submit">Confirm Telegram link</button></p></form>'
    )


def register_identity_pairing_routes(rt) -> None:
    """Register the UI for creating, claiming, and explicitly confirming a pairing."""

    @rt("/identity/telegram/pair")
    def get_telegram_pairing(request: Request):
        _, pairing_client = _api_client(request)
        if pairing_client is None:
            return _sign_in_required()
        return _page(
            "Connect Telegram to Janavani",
            '<p>Link only a Telegram account you control. A pairing code expires after a short time.</p>'
            '<p>Step 1: generate a one-time code, then send it to Janavani in a private Telegram chat.</p>'
            '<form action="/identity/telegram/pair" method="post">'
            '<button type="submit">Generate pairing code</button></form>'
            '<p>Generating a code does not link accounts. Linking completes only after Telegram claims the code and you explicitly confirm here.</p>',
        )

    @rt("/identity/telegram/pair")
    def post_start_telegram_pairing(request: Request):
        web_client, pairing_client = _api_client(request)
        if pairing_client is None:
            return _sign_in_required()
        try:
            challenge = pairing_client.issue()
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 403:
                return _page("Case access required", '<p>Your signed-in account does not have permission to link a Telegram identity.</p>', status_code=403)
            if exc.response.status_code == 503:
                return _page("Pairing unavailable", '<p>Cross-surface pairing requires the shared PostgreSQL identity store, which is not available in this runtime.</p>', status_code=503)
            return _page("Pairing could not start", '<p>Janavani could not create a pairing code. No link was created. Try again later.</p>', status_code=502)
        except (httpx.HTTPError, RuntimeError):
            return _page("Pairing temporarily unavailable", '<p>Janavani could not reach the identity service. No link was created.</p>', status_code=503)

        pairing_id = str(challenge.get("pairing_id", ""))
        code = str(challenge.get("code", ""))
        expires_at = str(challenge.get("expires_at", ""))
        if not pairing_id or not code or not expires_at:
            return _page("Pairing response invalid", '<p>Janavani returned an incomplete pairing response. Generate a new code later.</p>', status_code=502)
        safe_code = escape(code)
        body = (
            f'<p>Expires at (UTC): <time>{escape(expires_at)}</time></p>'
            f'<p>Your one-time code: <code>{safe_code}</code></p>'
            f'<p>Step 2: open a private chat with Janavani and send <code>/pair {safe_code}</code>. '
            "The bot will remove your command message when Telegram allows it.</p>"
            '<p>Step 3: after Telegram accepts the code, return here and explicitly confirm the link. '
            "The accounts are not linked until this confirmation succeeds.</p>"
            + _confirm_form(pairing_id)
        )
        return _page("Finish Telegram pairing", body)

    @rt("/identity/telegram/pair/{pairing_id}/confirm")
    def post_confirm_telegram_pairing(
        pairing_id: str,
        request: Request,
        explicit_confirmation: str = "",
    ):
        web_client, pairing_client = _api_client(request)
        if pairing_client is None:
            return _sign_in_required()
        if explicit_confirmation != "yes":
            return _page(
                "Confirmation required",
                _confirm_form(
                    pairing_id,
                    note='<p>Please check the confirmation box only if you initiated this link.</p>',
                ),
                status_code=400,
            )
        try:
            result = pairing_client.confirm(pairing_id)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 409:
                return _page(
                    "Pairing not ready",
                    '<p>The code may not have been claimed, may have expired, or may belong to another session. '
                    "Send the code with <code>/pair YOUR_CODE</code> in a private Telegram chat, then retry; "
                    "if it expired, generate a fresh code.</p>",
                    status_code=409,
                )
            if exc.response.status_code == 403:
                return _page("Confirmation denied", '<p>Your current authenticated account is not authorized to link Telegram.</p>', status_code=403)
            if exc.response.status_code == 503:
                return _page("Pairing unavailable", '<p>Shared PostgreSQL identity persistence is unavailable. No link was confirmed.</p>', status_code=503)
            return _page("Confirmation failed", '<p>Janavani could not confirm this pairing. Do not assume accounts are linked.</p>', status_code=502)
        except (httpx.HTTPError, RuntimeError, ValueError):
            return _page("Pairing temporarily unavailable", '<p>Janavani could not reach the identity service. No link confirmation was recorded.</p>', status_code=503)

        if result.get("linked") is not True or result.get("verified") is not True or result.get("provider") != "telegram":
            return _page("Confirmation unverified", '<p>The identity service did not confirm a verified Telegram link. Do not assume accounts are connected.</p>', status_code=502)
        return _page(
            "Telegram linked",
            '<p>Success: your verified Telegram identity is linked to this authenticated Janavani account.</p>'
            '<p>You can now continue an authorized Case from either surface. You can still use the WebApp without Telegram.</p>',
        )
