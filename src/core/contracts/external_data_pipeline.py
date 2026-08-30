"""Contracts for fetch, normalization, freshness and provenance stages."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class FreshnessStatus(str, Enum):
    UNKNOWN = "unknown"
    CURRENT = "current"
    STALE = "stale"


@dataclass(frozen=True)
class ExternalSourceEnvelope:
    provider_id: str
    dataset_id: str
    source_url: str
    retrieved_at: str
    raw: Any
    licence: Optional[str] = None


@dataclass(frozen=True)
class NormalizedExternalRecord:
    provider_id: str
    dataset_id: str
    record_id: str
    data: Mapping[str, Any]
    source_url: str
    retrieved_at: str
    licence: Optional[str]
    freshness: FreshnessStatus = FreshnessStatus.UNKNOWN
    provenance_verified: bool = False
