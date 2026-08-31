"""Shared authorization boundaries for Janavani capabilities."""

from .capabilities import DOCUMENT_GENERATE, DOCUMENT_TRANSMIT, PUBLIC_CAPABILITIES, PROTECTED_CAPABILITIES
from .policy import AuthorizationDecision, AuthorizationPolicy
from .transmission import TransmissionAuthorization, authorize_transmission

__all__ = [
    "AuthorizationDecision",
    "AuthorizationPolicy",
    "TransmissionAuthorization",
    "authorize_transmission",
    "DOCUMENT_GENERATE",
    "DOCUMENT_TRANSMIT",
    "PUBLIC_CAPABILITIES",
    "PROTECTED_CAPABILITIES",
]
