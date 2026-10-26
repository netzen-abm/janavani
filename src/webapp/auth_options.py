"""User-facing sign-in options, separated from WebApp composition."""
from __future__ import annotations

import os

from starlette.responses import HTMLResponse

from src.webapp.oidc_client import OIDCError, OIDCSettings


def register_auth_options_route(rt) -> None:
    """Advertise only configured identity methods; anonymous drafting stays public."""
    @rt("/auth/options")
    def get_auth_options():
        """Describe only account methods implemented or configured in this deployment."""
        try:
            OIDCSettings.from_environment()
            api_url = os.getenv("JANAVANI_WEB_API_URL", "").strip()
            oidc_ready = api_url.startswith("https://")
        except OIDCError:
            oidc_ready = False

        if oidc_ready:
            oidc_status = (
                "<p><strong>Configured:</strong> secure sign-in through the deployment's "
                "configured OpenID Connect provider. Provider reachability is checked when "
                "you start sign-in.</p><p><a href='/auth/login'>Continue to secure sign-in</a></p>"
            )
        else:
            oidc_status = (
                "<p><strong>Not configured in this deployment:</strong> Web account sign-in "
                "is unavailable until an OIDC provider and API trust settings are configured.</p>"
            )
        document = (
            "<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            "<meta name='viewport' content='width=device-width, initial-scale=1'>"
            "<title>Sign-in choices — Janavani</title></head><body><main>"
            "<h1>Choose how you use Janavani</h1>"
            "<p><strong>Anonymous use is available:</strong> you can generate a complaint, "
            "an RTI draft, or both without creating an account.</p>"
            "<section><h2>Web sign-in</h2>" + oidc_status + "</section>"
            "<section><h2>Telegram account</h2><p>In a private chat with the Janavani bot, "
            "use <code>/account</code> to opt in to account-based tracking when the shared "
            "identity database is configured. For a Web account and bot account to be "
            "connected, use the explicit pairing flow; Telegram identity alone does not "
            "automatically link accounts.</p><p>Email and mobile are not collected here.</p></section>"
            "<section><h2>Other choices</h2><p>Email one-time-code sign-in, SMS/mobile verification, "
            "and generated public/private-key sign-in are not available yet. Janavani will not "
            "ask you to paste a private key. These methods should appear only after verification, "
            "recovery, revocation, and security tests are complete.</p></section>"
            "<p><a href='/'>Return to anonymous drafting</a></p>"
            "</main></body></html>"
        )
        return HTMLResponse(document, headers={
            "Cache-Control": "no-store, private",
            "Pragma": "no-cache",
            "Referrer-Policy": "no-referrer",
            "X-Content-Type-Options": "nosniff",
            "Content-Security-Policy": "default-src 'none'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
            "X-Frame-Options": "DENY",
        })
