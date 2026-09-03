"""Provider-neutral authenticated session lifecycle.

This module stores only hashed opaque session identifiers in the server-side
session registry. Raw session tokens are returned once to the caller and are
never logged or placed in Principal.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import hashlib
import secrets
from threading import RLock
from typing import Dict, Optional

from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal


class InvalidSession(PermissionError):
    """Raised when an authenticated session is missing, expired, or revoked."""


@dataclass(frozen=True)
class SessionRecord:
    principal_id: str
    session_id: str
    token_hash: str
    authentication_method: AuthenticationMethod
    scopes: frozenset[str]
    capabilities: frozenset[str]
    expires_at: datetime
    revoked: bool = False


class SessionManager:
    """Minimal in-memory session manager with opaque bearer tokens.

    Persistence is intentionally left behind an interface. A production
    deployment may use an encrypted/managed session store without changing
    the Principal contract.
    """

    def __init__(self, ttl: timedelta = timedelta(minutes=15)):
        self._ttl = ttl
        self._sessions: Dict[str, SessionRecord] = {}
        self._lock = RLock()

    @staticmethod
    def _hash(token: str) -> str:
        return hashlib.sha256(token.encode("utf-8")).hexdigest()

    def create_session(
        self,
        principal_id: str,
        *,
        authentication_method: AuthenticationMethod,
        scopes: frozenset[str] = frozenset(),
        capabilities: frozenset[str] = frozenset(),
    ) -> tuple[str, SessionRecord]:
        session_id = secrets.token_urlsafe(24)
        raw_token = secrets.token_urlsafe(48)
        expires_at = datetime.now(timezone.utc) + self._ttl
        record = SessionRecord(
            principal_id=principal_id,
            session_id=session_id,
            token_hash=self._hash(raw_token),
            authentication_method=authentication_method,
            scopes=scopes,
            capabilities=capabilities,
            expires_at=expires_at,
        )
        with self._lock:
            self._sessions[session_id] = record
        return raw_token, record

    def resolve(self, session_id: str, raw_token: str, *, interface: str = "unknown") -> IdentityContext:
        with self._lock:
            record = self._sessions.get(session_id)
        if record is None or record.revoked:
            raise InvalidSession("session is invalid")
        if record.expires_at <= datetime.now(timezone.utc):
            raise InvalidSession("session is expired")
        if not secrets.compare_digest(record.token_hash, self._hash(raw_token)):
            raise InvalidSession("session is invalid")

        principal = Principal(
            principal_id=record.principal_id,
            identity_mode=IdentityMode.AUTHENTICATED,
            interface=interface,
            authentication_method=record.authentication_method,
            session_id=record.session_id,
            scopes=record.scopes,
            capabilities=record.capabilities,
        )
        return IdentityContext(principal=principal, request_id=None)

    def revoke(self, session_id: str) -> None:
        with self._lock:
            record = self._sessions.get(session_id)
            if record is not None:
                self._sessions[session_id] = SessionRecord(
                    principal_id=record.principal_id,
                    session_id=record.session_id,
                    token_hash=record.token_hash,
                    authentication_method=record.authentication_method,
                    scopes=record.scopes,
                    capabilities=record.capabilities,
                    expires_at=record.expires_at,
                    revoked=True,
                )
