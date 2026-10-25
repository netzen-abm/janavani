"""Web OIDC routes, encrypted login transaction, and short-lived API assertion minting."""
from __future__ import annotations
import base64, hashlib, hmac, json, os, secrets, time
from html import escape
from uuid import uuid4
from urllib.parse import urlsplit
from cryptography.fernet import Fernet, InvalidToken
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from src.webapp.oidc_client import (
    OIDCAuthenticationError, OIDCConfigurationError, OIDCError, OIDCSettings,
    authorization_url, exchange_authorization_code, new_login_transaction,
)

_TRANSACTION_COOKIE = "janavani_oidc_transaction"
_SESSION_IDENTITY = "janavani_identity"
_CITIZEN_CAPABILITIES = (
    "JNV-CIVIC-COMPLAINT", "case:read", "case:write", "case:review",
    "case:evidence", "evidence:register", "evidence:read", "document:review",
)


def session_secret_for_middleware() -> str:
    secret = os.getenv("JANAVANI_WEB_SESSION_SECRET", "").strip()
    if os.getenv("JANAVANI_RUNTIME_MODE", "development").lower() == "production":
        if len(secret) < 32:
            raise OIDCConfigurationError("Production WebApp requires JANAVANI_WEB_SESSION_SECRET")
        return secret
    return secret or secrets.token_urlsafe(48)


def validate_web_identity_configuration() -> None:
    """Keep OIDC client credentials scoped to the WebApp, not API or Telegram."""
    if os.getenv("JANAVANI_RUNTIME_MODE", "development").strip().lower() == "production":
        OIDCSettings.from_environment()
        api_url = urlsplit(os.getenv("JANAVANI_WEB_API_URL", "").strip())
        if api_url.scheme != "https" or not api_url.hostname or api_url.username or api_url.password or api_url.query or api_url.fragment:
            raise OIDCConfigurationError("Production WebApp requires an HTTPS JANAVANI_WEB_API_URL")


def _cipher(settings: OIDCSettings) -> Fernet:
    key = base64.urlsafe_b64encode(hashlib.sha256(
        ("janavani-oidc-transaction-v1:" + settings.web_session_secret).encode()
    ).digest())
    return Fernet(key)


def _page(title: str, message: str, *, status: int = 200) -> HTMLResponse:
    body = ("<!doctype html><html lang=\"en\"><head><meta charset=\"utf-8\">"
            "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">"
            f"<title>{escape(title)} — Janavani</title></head><body><main>"
            f"<h1>{escape(title)}</h1><p>{escape(message)}</p>"
            "<p><a href=\"/\">Return to Janavani</a></p></main></body></html>")
    return HTMLResponse(body, status_code=status, headers={
        "Cache-Control": "no-store, private", "Pragma": "no-cache",
        "Referrer-Policy": "no-referrer", "X-Content-Type-Options": "nosniff",
        "Content-Security-Policy": "default-src 'none'; form-action 'self'; base-uri 'none'; frame-ancestors 'none'",
    })


def _secure_cookie() -> bool:
    return os.getenv("JANAVANI_RUNTIME_MODE", "development").strip().lower() == "production"


def _clear_transaction(response: HTMLResponse | RedirectResponse) -> None:
    response.delete_cookie(_TRANSACTION_COOKIE, path="/auth/callback", secure=_secure_cookie(),
                           httponly=True, samesite="lax")


def api_assertion_for_session(session: dict) -> str | None:
    """Mint an API-scoped five-minute assertion from a server-verified Web session."""
    identity = session.get(_SESSION_IDENTITY)
    if not isinstance(identity, dict):
        return None
    principal = identity.get("principal_id")
    if not isinstance(principal, str) or not principal.startswith("janavani:oidc:"):
        return None
    secret = os.getenv("JANAVANI_IDENTITY_ASSERTION_SECRET", "").strip()
    issuer = os.getenv("JANAVANI_IDENTITY_ASSERTION_ISSUER", "").strip()
    audience = os.getenv("JANAVANI_IDENTITY_ASSERTION_AUDIENCE", "").strip()
    if len(secret) < 32 or not issuer or not audience:
        raise OIDCConfigurationError("Internal API assertion trust is not configured")
    now = int(time.time())
    payload = {
        "iss": issuer, "aud": audience, "sub": principal, "principal_id": principal,
        "provider": "oidc", "subject": principal, "authentication_method": "oidc",
        "iat": now, "exp": now + 300, "jti": uuid4().hex,
        "capabilities": list(_CITIZEN_CAPABILITIES), "scopes": [],
    }
    raw = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode()
    encoded = base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")
    signature = hmac.new(secret.encode(), encoded.encode("ascii"), hashlib.sha256).digest()
    signed = base64.urlsafe_b64encode(signature).rstrip(b"=").decode("ascii")
    return encoded + "." + signed


def register_identity_gateway_routes(rt) -> None:
    """Register OIDC login, exact callback, and explicit logout operations."""

    @rt("/auth/login")
    def get_auth_login():
        try:
            settings = OIDCSettings.from_environment()
            transaction = new_login_transaction()
            url = authorization_url(settings, transaction)
            encrypted = _cipher(settings).encrypt(json.dumps(transaction, separators=(",", ":")).encode()).decode("ascii")
        except OIDCError:
            return _page("Sign-in unavailable", "Janavani sign-in is not configured or the identity provider is unavailable.", status=503)
        response = RedirectResponse(url, status_code=303, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
        response.set_cookie(_TRANSACTION_COOKIE, encrypted, max_age=600, path="/auth/callback",
                            secure=_secure_cookie(), httponly=True, samesite="lax")
        return response

    @rt("/auth/callback")
    def get_auth_callback(request: Request, code: str = "", state: str = "", error: str = ""):
        cookie = request.cookies.get(_TRANSACTION_COOKIE, "")
        try:
            settings = OIDCSettings.from_environment()
            if (error or not code or not state or not cookie or
                    len(request.query_params.getlist("code")) != 1 or
                    len(request.query_params.getlist("state")) != 1):
                raise OIDCAuthenticationError("Authorization response is incomplete")
            transaction = json.loads(_cipher(settings).decrypt(cookie.encode("ascii"), ttl=600))
            if not isinstance(transaction, dict) or not isinstance(transaction.get("state"), str):
                raise OIDCAuthenticationError("Login transaction is invalid")
            if not hmac.compare_digest(state, transaction["state"]):
                raise OIDCAuthenticationError("OIDC state validation failed")
            response_issuers = request.query_params.getlist("iss")
            if len(response_issuers) > 1 or (response_issuers and response_issuers[0] != settings.issuer_url):
                raise OIDCAuthenticationError("OIDC response issuer is invalid")
            claims = exchange_authorization_code(settings, code, transaction)
            if not isinstance(claims, dict):
                raise OIDCAuthenticationError("OIDC ID-token claims are invalid")
            subject = claims.get("sub")
            if not isinstance(subject, str) or not subject:
                raise OIDCAuthenticationError("OIDC subject is invalid")
            principal = "janavani:oidc:" + hashlib.sha256(
                (settings.issuer_url + "\0" + subject).encode("utf-8")
            ).hexdigest()
        except (OIDCError, InvalidToken, UnicodeDecodeError, ValueError, TypeError, KeyError):
            # Do not echo provider response bodies, codes, tokens, or internal endpoints.
            response = _page("Sign-in could not be completed", "The identity response was invalid, expired, or could not be verified.", status=401)
            _clear_transaction(response)
            return response
        request.session.clear()
        request.session[_SESSION_IDENTITY] = {
            "principal_id": principal, "provider": "oidc", "authentication_method": "oidc"
        }
        response = RedirectResponse("/", status_code=303, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
        _clear_transaction(response)
        return response

    @rt("/auth/logout", methods=["POST"])
    def post_auth_logout(request: Request):
        request.session.clear()
        response = RedirectResponse("/", status_code=303, headers={"Cache-Control": "no-store", "Referrer-Policy": "no-referrer"})
        response.delete_cookie("janavani_identity_assertion", path="/", secure=_secure_cookie(), httponly=True, samesite="lax")
        _clear_transaction(response)
        return response
