"""Shared AI provider composition.

Concrete AI providers are selected and instantiated only at this boundary.
Capabilities and services depend on the provider-neutral AIProvider contract,
while this module owns provider dependency and runtime construction.
"""
from __future__ import annotations

import requests

from src.ai.provider import AIProvider
from src.ai.providers.huggingface_translation import HuggingFaceTranslationProvider
from src.ai.providers.openrouter import OpenRouterProvider


def create_openrouter_provider(
    http_session: requests.Session | None = None,
) -> AIProvider:
    """Compose the configured OpenRouter adapter behind AIProvider."""
    return OpenRouterProvider(http_session)


def create_translation_provider(
    http_session: requests.Session | None = None,
) -> AIProvider:
    """Compose the configured translation adapter behind AIProvider."""
    return HuggingFaceTranslationProvider(http_session)
