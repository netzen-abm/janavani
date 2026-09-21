"""Compatibility marker for the retired legacy case migration service.

Case creation, ownership, lifecycle and consent now belong to canonical
capabilities. Legacy Telegram sessions must be migrated at the adapter boundary
before invoking those capabilities.
"""
from src.capabilities.civic_case import CivicCaseCapability

__all__ = ["CivicCaseCapability"]
