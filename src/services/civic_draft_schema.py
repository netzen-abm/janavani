"""Validation boundary for untrusted AI-generated civic-draft fields.

Only a small allow-list of editable prose is accepted. Legal citations, authority
identifiers, evidence references, deadlines and verification claims are never
accepted from model output.
"""
from __future__ import annotations

import json
from typing import Any


class InvalidAIDraftOutput(ValueError):
    """Raised when a provider response is not a valid civic-draft proposal."""


_TEXT_FIELDS = {
    "proposal_or_notice": 6_000,
    "subject": 200,
}
_LIST_FIELDS = {
    "part_i_interrogatories": (12, 800),
    "requested_conditions": (12, 800),
    "remedies_reserved": (8, 500),
}


def _bounded_text(value: Any, field: str, max_length: int, *, required: bool = False) -> str:
    if value is None and not required:
        return ""
    if not isinstance(value, str):
        raise InvalidAIDraftOutput(f"AI field {field} must be text")
    value = value.strip()
    if required and not value:
        raise InvalidAIDraftOutput(f"AI field {field} is required")
    if len(value) > max_length:
        raise InvalidAIDraftOutput(f"AI field {field} exceeds the length limit")
    return value


def _string_list(value: Any, field: str, *, max_items: int, max_length: int) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, list) or len(value) > max_items:
        raise InvalidAIDraftOutput(f"AI field {field} must be a bounded list")
    result = []
    for item in value:
        cleaned = _bounded_text(item, field, max_length, required=True)
        result.append(cleaned)
    return result


def normalize_provider_draft(payload: dict[str, Any], *, fallback_subject: str) -> dict[str, Any]:
    """Extract and validate the supported JSON response shape from OpenRouter."""
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
        raise InvalidAIDraftOutput("AI provider returned no draft choice")
    message = choices[0].get("message")
    if not isinstance(message, dict) or not isinstance(message.get("content"), str):
        raise InvalidAIDraftOutput("AI provider returned no text draft")
    raw = message["content"].strip()
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
        if raw.endswith("```"):
            raw = raw[:-3].strip()
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise InvalidAIDraftOutput("AI provider returned invalid JSON") from exc
    if not isinstance(decoded, dict):
        raise InvalidAIDraftOutput("AI draft must be a JSON object")

    subject = _bounded_text(
        decoded.get("subject", fallback_subject), "subject", _TEXT_FIELDS["subject"],
        required=True,
    )
    result: dict[str, Any] = {
        "subject": subject,
        "proposal_or_notice": _bounded_text(
            decoded.get("proposal_or_notice", ""),
            "proposal_or_notice",
            _TEXT_FIELDS["proposal_or_notice"],
        ),
    }
    for field, (max_items, max_length) in _LIST_FIELDS.items():
        result[field] = _string_list(
            decoded.get(field, []),
            field,
            max_items=max_items,
            max_length=max_length,
        )
    if not any(
        result[field]
        for field in ("proposal_or_notice", "part_i_interrogatories", "requested_conditions", "remedies_reserved")
    ):
        raise InvalidAIDraftOutput("AI draft contains no usable draft sections")
    return result
