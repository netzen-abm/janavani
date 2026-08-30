"""Shared privacy gate for outbound AI/agent requests.

The gateway is deliberately allow-list based: callers must provide already
sanitized context, and only explicitly permitted fields are forwarded. It
never accepts a raw Case/Evidence object and never performs implicit uploads.
"""

from dataclasses import dataclass
from typing import Any, Mapping


ALLOWED_CONTEXT_FIELDS = frozenset({
    "task",
    "issue_type",
    "jurisdiction",
    "public_facts",
    "document_purpose",
    "language",
})


@dataclass(frozen=True)
class PrivacyDecision:
    allowed: bool
    context: dict[str, Any]
    reason: str | None = None


class PrivacyGateway:
    """Fail-closed gateway for outbound AI/agent context."""

    def sanitize(self, context: Mapping[str, Any]) -> PrivacyDecision:
        keys = set(context)
        unexpected = keys - ALLOWED_CONTEXT_FIELDS
        if unexpected:
            return PrivacyDecision(False, {}, "unexpected_or_private_fields")

        sanitized: dict[str, Any] = {}
        for key, value in context.items():
            if value is None:
                continue
            if isinstance(value, (str, int, float, bool)):
                sanitized[key] = value
            elif key == "public_facts" and isinstance(value, list) and all(
                isinstance(item, str) for item in value
            ):
                sanitized[key] = list(value)
            else:
                return PrivacyDecision(False, {}, "unsupported_context_value")

        return PrivacyDecision(True, sanitized)

    def authorize_ai(self, context: Mapping[str, Any], user_opted_in: bool) -> PrivacyDecision:
        if not user_opted_in:
            return PrivacyDecision(False, {}, "ai_not_enabled_by_user")
        return self.sanitize(context)
