"""Hard privacy gate for all AI and Agentic AI communication.

This gateway is intentionally conservative: personal data is never forwarded
through an AI/agent provider. Callers must supply already-sanitized, public or
synthetic context. The gateway rejects rather than attempting probabilistic
PII detection as its sole protection.
"""
from __future__ import annotations
import re
from typing import Any
from pydantic import BaseModel, Field


# Defense-in-depth detectors. They are not the policy itself: callers should
# construct sanitized payloads from allow-listed fields before reaching here.
_PATTERNS = (
    re.compile(r"\b\d{12}\b"),                    # Aadhaar-like number
    re.compile(r"\b\d{10}\b"),                    # Indian mobile-like number
    re.compile(r"\b[6-9]\d{9}\b"),
    re.compile(r"\b[A-Z]{5}\d{4}[A-Z]\b"),        # PAN-like identifier
    re.compile(r"\b\d{4}[ -]?\d{4}[ -]?\d{4}\b"), # card-like identifier
    re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+"),
)


class PrivacyViolation(ValueError):
    """Raised when a remote AI/agent boundary receives prohibited data."""


class SanitizedPayload(BaseModel):
    purpose: str = Field(min_length=1, max_length=200)
    text: str = Field(default="", max_length=50000)
    context: dict[str, Any] = Field(default_factory=dict)
    data_classification: str = "non_personal"


def _contains_obvious_pii(value: str) -> bool:
    return any(pattern.search(value) for pattern in _PATTERNS)


def _walk(value: Any) -> bool:
    if isinstance(value, str):
        return _contains_obvious_pii(value)
    if isinstance(value, dict):
        return any(_walk(k) or _walk(v) for k, v in value.items())
    if isinstance(value, (list, tuple, set)):
        return any(_walk(item) for item in value)
    return False


def sanitize_for_ai(*, purpose: str, text: str = "", context: dict[str, Any] | None = None) -> SanitizedPayload:
    context = context or {}
    if _contains_obvious_pii(text) or _walk(context):
        raise PrivacyViolation("AI/Agent communication blocked: personal data detected")
    return SanitizedPayload(purpose=purpose, text=text, context=context)


def assert_non_personal(payload: SanitizedPayload) -> None:
    if payload.data_classification != "non_personal":
        raise PrivacyViolation("AI/Agent communication blocked: payload is not non-personal")
    if _contains_obvious_pii(payload.text) or _walk(payload.context):
        raise PrivacyViolation("AI/Agent communication blocked: personal data detected")
