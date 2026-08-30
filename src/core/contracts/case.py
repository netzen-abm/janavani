"""Channel-neutral case contract for civic actions.

This module deliberately contains workflow metadata and references rather than
raw identity data. Access channels (Telegram, WebApp, etc.) should adapt into
this contract instead of implementing case semantics themselves.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class CaseStatus(str, Enum):
    DRAFT = "draft"
    UNDERSTANDING = "understanding"
    AUTHORITY_PENDING = "authority_pending"
    AUTHORITY_VERIFICATION = "authority_verification"
    REVIEW = "review"
    DOCUMENT_READY = "document_ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class VerificationStatus(str, Enum):
    UNKNOWN = "unknown"
    CITIZEN_PROVIDED = "citizen_provided"
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


@dataclass
class AuthorityReference:
    """Authority selected or supplied for a case."""

    authority_id: Optional[str] = None
    name: Optional[str] = None
    location: Optional[str] = None
    source: str = "system"
    verification: VerificationStatus = VerificationStatus.UNKNOWN


@dataclass
class Case:
    """Canonical case state shared by all access channels."""

    case_id: str
    status: CaseStatus = CaseStatus.DRAFT
    issue_text: str = ""
    category: Optional[str] = None
    department: Optional[str] = None
    authority: Optional[AuthorityReference] = None
    evidence_refs: List[str] = field(default_factory=list)
    legal_reference_refs: List[str] = field(default_factory=list)
    document_refs: List[str] = field(default_factory=list)
    identity_mode: str = "anonymous"
    consent_refs: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def touch(self) -> None:
        """Update the case modification timestamp."""
        self.updated_at = datetime.now(timezone.utc)

    def set_authority(self, authority: AuthorityReference) -> None:
        self.authority = authority
        self.status = CaseStatus.AUTHORITY_VERIFICATION
        self.touch()

    def add_evidence_ref(self, reference: str) -> None:
        if reference not in self.evidence_refs:
            self.evidence_refs.append(reference)
        self.touch()

    def add_document_ref(self, reference: str) -> None:
        if reference not in self.document_refs:
            self.document_refs.append(reference)
        self.touch()
