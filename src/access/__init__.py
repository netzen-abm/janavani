"""Shared access-control primitives."""

from .authorization import (
    AuthorizationDecision,
    AuthorizationPolicy,
    AuthorizationRequest,
    authorize,
)

__all__ = [
    "AuthorizationDecision",
    "AuthorizationPolicy",
    "AuthorizationRequest",
    "authorize",
]
