"""Shared application composition for provider-neutral Janavani capabilities.

Access surfaces compose dependencies here; domain and capability code never
selects a concrete provider. Each process owns one repository instance and
passes it to its adapters. Durable providers are required for cross-process
and cross-surface continuity.
"""
from __future__ import annotations

from src.capabilities.civic_case import CivicCaseCapability
from src.storage.repositories.civic_case import CivicCaseRepository
from src.storage.repositories.provider import create_civic_case_repository


def create_case_repository() -> CivicCaseRepository:
    """Compose the configured Case repository once for an application process."""
    return create_civic_case_repository()


def create_case_capability(repository: CivicCaseRepository) -> CivicCaseCapability:
    """Compose the shared Civic Case capability over an injected repository."""
    return CivicCaseCapability(repository)
