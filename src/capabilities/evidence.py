"""Canonical provider- and surface-neutral Evidence capability."""
from __future__ import annotations

from dataclasses import dataclass
from uuid import uuid4

from src.access.authorization import AuthorizationDecision, AuthorizationRequest, authorize
from src.capabilities.civic_case import CivicCaseCapability, CivicCaseResult
from src.core.evidence import EvidenceObject, EvidenceRepository, EvidenceSource, validate_sha256
from src.identity.context import IdentityContext

CAPABILITY_ID = "case:evidence"


@dataclass(frozen=True)
class EvidenceCreateRequest:
    evidence_type: str
    storage_ref: str
    sha256: str
    received_at: str
    captured_at: str | None = None
    source_description: str | None = None
    provenance: tuple[EvidenceSource, ...] = ()
    access_policy_ref: str | None = None
    retention_policy_ref: str | None = None
    status: str = "ACTIVE"


class EvidenceCapability:
    """Shared evidence registration and Case-linkage boundary.

    The capability stores evidence metadata only. Binary content remains behind
    a storage reference, and registration never uploads or transmits content.
    """

    def __init__(self, repository: EvidenceRepository, case_capability: CivicCaseCapability) -> None:
        self._repository = repository
        self._cases = case_capability

    def register(self, request: EvidenceCreateRequest, *, identity: IdentityContext) -> EvidenceObject:
        """Register evidence metadata without uploading or transmitting content."""
        self._authorize(identity, "evidence:register")
        evidence_type = request.evidence_type.strip()
        storage_ref = request.storage_ref.strip()
        if not evidence_type:
            raise ValueError("Evidence type is required")
        if not storage_ref:
            raise ValueError("Evidence storage reference is required")
        sha256 = validate_sha256(request.sha256)
        evidence = EvidenceObject(
            evidence_id=f"evidence-{uuid4().hex}", evidence_type=evidence_type,
            storage_ref=storage_ref, sha256=sha256, received_at=request.received_at,
            captured_at=request.captured_at, source_description=request.source_description,
            provenance=request.provenance, access_policy_ref=request.access_policy_ref,
            retention_policy_ref=request.retention_policy_ref, status=request.status,
        )
        self._repository.save(evidence)
        return evidence

    def attach(self, case_id: str, evidence_id: str, *, identity: IdentityContext,
               source_channel: str | None = None) -> CivicCaseResult:
        """Attach registered evidence to an owned Case; never transmit it."""
        evidence = self._repository.get(evidence_id)
        if evidence is None:
            raise LookupError("Evidence not found")
        return self._cases.add_evidence(case_id, evidence.evidence_id,
                                        identity=identity, source_channel=source_channel)

    def get_for_case(self, case_id: str, *, identity: IdentityContext) -> tuple[EvidenceObject, ...]:
        """Return evidence metadata only for an owned Case."""
        case = self._cases.get_owned(case_id, identity=identity)
        if case is None:
            raise LookupError("Case not found")
        self._authorize(identity, "evidence:read")
        return tuple(
            evidence for evidence_id in case.evidence_refs
            if (evidence := self._repository.get(evidence_id)) is not None
        )

    @staticmethod
    def _authorize(identity: IdentityContext, action: str) -> None:
        decision = authorize(AuthorizationRequest(context=identity, capability=CAPABILITY_ID, action=action))
        if decision is not AuthorizationDecision.ALLOW:
            raise PermissionError("Identity is not authorized for evidence access")
