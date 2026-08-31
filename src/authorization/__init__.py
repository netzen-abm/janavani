"""Shared authorization boundary for Janavani capabilities."""

from .capabilities import DOCUMENT_GENERATE, PUBLIC_CAPABILITIES
from .endpoint import AuthorizationDenied, authorize_capability
from .policy import AuthorizationPolicy

__all__ = [
    "DOCUMENT_GENERATE",
    "PUBLIC_CAPABILITIES",
    "AuthorizationDenied",
    "AuthorizationPolicy",
    "authorize_capability",
]
