"""Shared Evidence-to-Case integration.

Evidence bytes remain outside the canonical Case object. The Case stores only
stable evidence references and safe metadata. This prevents raw personal or
sensitive evidence from entering shared orchestration or AI context by default.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional

from src.core.contracts.case import Case


@dataclass(frozen=True)
class EvidenceReference:
    evidence_id: str
    kind: str
    local: bool = True
    sensitive: bool = False
    content_hash: Optional[str] = None


class SharedEvidenceCaseService:
    """Attach evidence references without copying evidence payloads into Case."""

    def attach(self, case: Case, evidence: EvidenceReference) -> Case:
        if not evidence.evidence_id.strip():
            raise ValueError("evidence_id is required")
        case.add_evidence_ref(evidence.evidence_id)
        return case

    @staticmethod
    def ai_context_metadata(evidence: EvidenceReference) -> Mapping[str, object]:
        """Return metadata only; raw evidence never enters AI context here."""
        return {
            "evidence_id": evidence.evidence_id,
            "kind": evidence.kind,
            "local": evidence.local,
            "sensitive": evidence.sensitive,
            "content_hash": evidence.content_hash,
        }
