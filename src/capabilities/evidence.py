"""Channel-neutral Evidence capability contract."""

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
    def add(
        self,
        *,
        case_id: str,
        evidence_type: str,
        source_channel: str,
        filename: str | None = None,
        content_type: str | None = None,
        storage_reference: str | None = None,
        sha256: str | None = None,
        metadata: dict | None = None,
    ) -> EvidenceResult: ...

    def list(self, *, case_id: str) -> list[EvidenceItem]: ...
