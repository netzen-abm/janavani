"""Provider-configured OIDC code/PKCE client; never stores provider tokens."""
from __future__ import annotations
import base64, hashlib, hmac, os, secrets
from dataclasses import dataclass, field
from urllib.parse import urlencode, urlsplit
import httpx
import jwt

_ALLOWED_ALGORITHMS = frozenset({"RS256", "ES256", "PS256"})


class OIDCError(RuntimeError):
    """Safe parent for sign-in/configuration failures."""


class OIDCConfigurationError(OIDCError):
    """Trusted OIDC configuration is missing or inconsistent."""


class OIDCProviderUnavailable(OIDCError):
    """The configured identity provider could not be reached."""


class OIDCAuthenticationError(OIDCError):
    """An authorization response or ID token failed validation."""


@dataclass(frozen=True)
class OIDCSettings:
    issuer_url: str
    client_id: str
    client_secret: str = field(repr=False)
    redirect_uri: str
    web_session_secret: str = field(repr=False)
    assertion_secret: str = field(repr=False)
    assertion_issuer: str
    assertion_audience: str

    @classmethod
    def from_environment(cls) -> "OIDCSettings":
        names = ("JANAVANI_OIDC_ISSUER_URL", "JANAVANI_OIDC_CLIENT_ID",
                 "JANAVANI_OIDC_CLIENT_SECRET", "JANAVANI_OIDC_REDIRECT_URI",
                 "JANAVANI_WEB_SESSION_SECRET", "JANAVANI_IDENTITY_ASSERTION_SECRET",
                 "JANAVANI_IDENTITY_ASSERTION_ISSUER", "JANAVANI_IDENTITY_ASSERTION_AUDIENCE")
        values = {name: os.getenv(name, "").strip() for name in names}
        if any(not value for value in values.values()):
            raise OIDCConfigurationError("Web sign-in is not fully configured")
        if any(len(values[name]) < 32 for name in
               ("JANAVANI_WEB_SESSION_SECRET", "JANAVANI_IDENTITY_ASSERTION_SECRET")):
            raise OIDCConfigurationError("Web session and assertion secrets must be at least 32 characters")
        issuer = values["JANAVANI_OIDC_ISSUER_URL"]
        i = urlsplit(issuer)
        if i.scheme != "https" or not i.hostname or i.username or i.password or i.query or i.fragment:
            raise OIDCConfigurationError("OIDC issuer must be a clean HTTPS URL")
        redirect = urlsplit(values["JANAVANI_OIDC_REDIRECT_URI"])
        local = redirect.scheme == "http" and redirect.hostname in {"localhost", "127.0.0.1", "::1"}
        if (not redirect.hostname or redirect.path != "/auth/callback" or redirect.username or
                redirect.password or redirect.query or redirect.fragment):
            raise OIDCConfigurationError("OIDC redirect URI must end exactly in /auth/callback")
        if redirect.scheme != "https" and not (local and os.getenv("JANAVANI_RUNTIME_MODE", "development").lower() != "production"):
            raise OIDCConfigurationError("OIDC redirect URI must use HTTPS outside local development")
        return cls(issuer, values["JANAVANI_OIDC_CLIENT_ID"], values["JANAVANI_OIDC_CLIENT_SECRET"],
                   values["JANAVANI_OIDC_REDIRECT_URI"], values["JANAVANI_WEB_SESSION_SECRET"],
                   values["JANAVANI_IDENTITY_ASSERTION_SECRET"], values["JANAVANI_IDENTITY_ASSERTION_ISSUER"],
                   values["JANAVANI_IDENTITY_ASSERTION_AUDIENCE"])


def _https_endpoint(value: object, name: str) -> str:
    if not isinstance(value, str):
        raise OIDCConfigurationError(f"OIDC metadata has no valid {name}")
    p = urlsplit(value)
    if p.scheme != "https" or not p.hostname or p.username or p.password or p.fragment:
        raise OIDCConfigurationError(f"OIDC {name} must use HTTPS")
    return value


def load_discovery(settings: OIDCSettings) -> dict[str, object]:
    url = settings.issuer_url.rstrip("/") + "/.well-known/openid-configuration"
    try:
        response = httpx.get(url, timeout=5.0)
        response.raise_for_status()
        metadata = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise OIDCProviderUnavailable("The configured identity provider is unavailable") from exc
    if not isinstance(metadata, dict) or metadata.get("issuer") != settings.issuer_url:
        raise OIDCConfigurationError("OIDC discovery issuer does not match configuration")
    for key in ("authorization_endpoint", "token_endpoint", "jwks_uri"):
        _https_endpoint(metadata.get(key), key)
    return metadata


def new_login_transaction() -> dict[str, str]:
    verifier = secrets.token_urlsafe(48)
    challenge = base64.urlsafe_b64encode(hashlib.sha256(verifier.encode("ascii")).digest()).rstrip(b"=").decode()
    return {"state": secrets.token_urlsafe(32), "nonce": secrets.token_urlsafe(32),
            "code_verifier": verifier, "code_challenge": challenge}


def authorization_url(settings: OIDCSettings, transaction: dict[str, str]) -> str:
    endpoint = str(load_discovery(settings)["authorization_endpoint"])
    params = urlencode({"client_id": settings.client_id, "redirect_uri": settings.redirect_uri,
                        "response_type": "code", "scope": "openid", "state": transaction["state"],
                        "nonce": transaction["nonce"], "code_challenge": transaction["code_challenge"],
                        "code_challenge_method": "S256"})
    return endpoint + ("&" if "?" in endpoint else "?") + params


def exchange_authorization_code(settings: OIDCSettings, code: str, transaction: dict[str, str]) -> dict[str, object]:
    if not code or len(code) > 4096:
        raise OIDCAuthenticationError("OIDC authorization code is invalid")
    metadata = load_discovery(settings)
    try:
        response = httpx.post(str(metadata["token_endpoint"]), data={
            "grant_type": "authorization_code", "code": code, "redirect_uri": settings.redirect_uri,
            "code_verifier": transaction["code_verifier"]},
            auth=(settings.client_id, settings.client_secret), headers={"Accept": "application/json"}, timeout=10.0)
        response.raise_for_status()
        tokens = response.json()
    except (httpx.HTTPError, ValueError) as exc:
        raise OIDCProviderUnavailable("The identity provider could not complete sign-in") from exc
    if not isinstance(tokens, dict) or not isinstance(tokens.get("id_token"), str):
        raise OIDCAuthenticationError("OIDC response did not contain an ID token")
    return verify_id_token(settings, str(metadata["jwks_uri"]), tokens["id_token"], transaction["nonce"])


def verify_id_token(settings: OIDCSettings, jwks_uri: str, token: str, expected_nonce: str) -> dict[str, object]:
    """Enforce an asymmetric algorithm allowlist, issuer, audience, expiry, signature and nonce."""
    endpoint = _https_endpoint(jwks_uri, "jwks_uri")
    try:
        header = jwt.get_unverified_header(token)
        algorithm, kid = header.get("alg"), header.get("kid")
        if algorithm not in _ALLOWED_ALGORITHMS or not isinstance(kid, str) or not kid:
            raise OIDCAuthenticationError("OIDC ID-token header is invalid")
        response = httpx.get(endpoint, timeout=5.0)
        response.raise_for_status()
        doc = response.json()
        keys = doc.get("keys", []) if isinstance(doc, dict) else []
        matches = [key for key in keys if isinstance(key, dict) and key.get("kid") == kid
                   and key.get("use", "sig") == "sig" and key.get("alg", algorithm) == algorithm]
        if len(matches) != 1:
            raise OIDCAuthenticationError("OIDC signing key is missing or ambiguous")
        public_key = jwt.PyJWK.from_dict(matches[0], algorithm=algorithm).key
        claims = jwt.decode(token, public_key, algorithms=[algorithm], audience=settings.client_id,
                            issuer=settings.issuer_url, leeway=60,
                            options={"require": ["exp", "iat", "iss", "sub", "aud", "nonce"]})
    except OIDCAuthenticationError:
        raise
    except (httpx.HTTPError, ValueError, TypeError, jwt.PyJWTError) as exc:
        raise OIDCAuthenticationError("OIDC ID-token validation failed") from exc
    subject, nonce, audience = claims.get("sub"), claims.get("nonce"), claims.get("aud")
    if not isinstance(subject, str) or not subject or len(subject) > 255:
        raise OIDCAuthenticationError("OIDC subject is invalid")
    if not isinstance(nonce, str) or not hmac.compare_digest(nonce, expected_nonce):
        raise OIDCAuthenticationError("OIDC nonce validation failed")
    if isinstance(audience, list) and len(audience) > 1 and claims.get("azp") != settings.client_id:
        raise OIDCAuthenticationError("OIDC authorized party is invalid")
    return claims
