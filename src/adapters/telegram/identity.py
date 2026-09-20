"""Canonical identity adapter for the Telegram surface."""
from __future__ import annotations
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal

def identity_for_telegram_user(user_id: int) -> IdentityContext:
    """Return the single canonical opaque principal for a Telegram user."""
    if user_id <= 0:
        raise ValueError("Telegram user identity is required")
    return IdentityContext(
        principal=Principal(
            principal_id=f"telegram:{user_id}",
            identity_mode=IdentityMode.ANONYMOUS,
            interface="telegram",
            authentication_method=AuthenticationMethod.NONE,
            session_id=str(user_id),
            capabilities=frozenset({"JNV-CIVIC-COMPLAINT"}),
        )
    )
