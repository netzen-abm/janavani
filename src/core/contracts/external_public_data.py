"""Shared contract for external public civic-data providers.

Providers supply contextual data only. They do not establish legal conclusions
or authoritative responsibility unless independently verified by JanaVani's
source-verification layer.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Optional


class ProviderVerificationStatus(str, Enum):
    UNVERIFIED = "unverified"
    VERIFIED = "verified"
    STALE = "stale"


@dataclass(frozen=True)
class ExternalDataRecord:
    provider_id: str
    dataset_id: str
    record_id: str
    jurisdiction: Optional[str]
    data: Mapping[str, Any]
    source_url: str
    licence: Optional[str] = None
    retrieved_at: Optional[str] = None
    verification: ProviderVerificationStatus = ProviderVerificationStatus.UNVERIFIED

    @property
    def usable_as_context(self) -> bool:
        return self.verification != ProviderVerificationStatus.STALE

    @property
    def usable_as_authority(self) -> bool:
        return self.verification == ProviderVerificationStatus.VERIFIED
