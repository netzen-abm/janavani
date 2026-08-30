"""Channel-neutral, local-first Evidence capability contract.

Evidence bytes remain on the citizen device by default. The capability records
only minimal non-sensitive metadata needed to refer to evidence. Any future
transmission must be explicitly authorized and pass minimization, scrubbing,
encoding and encryption before leaving the device.
"""

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class EvidenceItem:
    evidence_id: str
    case_id: str
    evidence_type: str
    source_channel: str
    created_at: str
    filename: str | None = None
    content_type: str | None = None
    storage_reference: str | None = None
    sha256: str | None = None
    metadata: dict | None = None


@dataclass(frozen=True)
class EvidenceResult:
    ok: bool
    evidence: EvidenceItem | None = None
    error_code: str | None = None
    message: str | None = None


class EvidenceCapability(Protocol):
    def register_local(
        self,
        *,
        case_id: str,
        evidence_type: str,
        source_channel: str,
        filename: str | None = None,
        content_type: str | None = None,
        local_reference: str | None = None,
        sha256: str | None = None,
        metadata: dict | None = None,
    ) -> EvidenceResult: ...

    def list(self, *, case_id: str) -> list[EvidenceItem]: ...

    def prepare_authorized_transmission(
        self,
        *,
        evidence_id: str,
        authorization_reference: str,
    ) -> EvidenceResult: ...
