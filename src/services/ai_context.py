"""Build strictly allow-listed context for remote AI/agent providers.

This module intentionally does not attempt to redact arbitrary Case objects.
Callers must opt into a small, non-personal schema. Personal case/profile data
must remain on the user's device.
"""
from __future__ import annotations

from typing import Any

from src.platform.privacy_gateway import SanitizedPayload, sanitize_for_ai

_ALLOWED_CONTEXT_KEYS = frozenset({
    "task_type",
    "document_type",
    "language",
    "jurisdiction_level",
    "public_authority_name",
    "public_source_urls",
    "public_facts",
    "requested_output",
})


def build_non_personal_ai_context(
    *,
    purpose: str,
    task_type: str,
    document_type: str | None = None,
    language: str | None = None,
    jurisdiction_level: str | None = None,
    public_authority_name: str | None = None,
    public_source_urls: list[str] | None = None,
    public_facts: list[str] | None = None,
    requested_output: str | None = None,
) -> SanitizedPayload:
    """Create the only supported remote-AI context shape.

    Values are restricted to explicitly public/non-personal fields and then
    passed through the hard privacy gateway as defense in depth.
    """
    context: dict[str, Any] = {"task_type": task_type}
    optional_values = {
        "document_type": document_type,
        "language": language,
        "jurisdiction_level": jurisdiction_level,
        "public_authority_name": public_authority_name,
        "public_source_urls": public_source_urls,
        "public_facts": public_facts,
        "requested_output": requested_output,
    }
    context.update({k: v for k, v in optional_values.items() if v is not None})
    context = {k: v for k, v in context.items() if k in _ALLOWED_CONTEXT_KEYS}
    return sanitize_for_ai(purpose=purpose, context=context)
