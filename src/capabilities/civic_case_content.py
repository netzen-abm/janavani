"""Persistence/content boundary for the canonical Civic Case capability."""
from __future__ import annotations

from src.access.authorization import AuthorizationDecision
from src.capabilities.civic_case_contract import CivicCaseResult
from src.core.civic_case import CivicCase
from src.core.execution import CapabilityExecutionContext
from src.identity.context import IdentityContext
from src.storage.repositories.case_content import CaseContent


class CivicCaseContentMixin:
    """Own the boundary between lifecycle metadata and citizen-authored content."""

    def hydrate_transient_content(
        self,
        case_id: str,
        *,
        identity: IdentityContext,
        subject: str | None = None,
        narrative: str | None = None,
        claims: tuple[dict[str, object], ...] = (),
        jurisdiction: dict[str, object] | None = None,
    ) -> None:
        case = self._repository.get(case_id, principal_id=identity.principal.principal_id)
        if case is None or case.created_by != identity.principal.principal_id:
            raise LookupError("Case not found")
        existing = self._content.get(case_id, principal_id=identity.principal.principal_id)
        self._content.save(
            case_id,
            CaseContent(
                subject=subject.strip() if subject is not None else (existing.subject if existing else ""),
                narrative=narrative.strip() if narrative is not None else (existing.narrative if existing else ""),
                claims=tuple(dict(claim) for claim in claims) if claims else (existing.claims if existing else ()),
                jurisdiction=dict(jurisdiction) if jurisdiction is not None else (existing.jurisdiction if existing else {}),
            ),
            principal_id=identity.principal.principal_id,
        )

    def get_owned(self, case_id: str, *, identity: IdentityContext) -> CivicCase | None:
        case = self._repository.get(case_id, principal_id=identity.principal.principal_id)
        if case is None or case.created_by != identity.principal.principal_id:
            return None
        content = self._content.get(case_id, principal_id=identity.principal.principal_id)
        if content is not None:
            # Keep durable Case.subject as lifecycle metadata. Citizen-authored subject
            # remains available to document/content consumers without mutating the aggregate
            # identity used by cross-surface contracts.
            # Rehydrate citizen-authored fields only for the in-memory aggregate used by
            # lifecycle validation; lifecycle persistence normalizes these fields afterward.
            case.subject = content.subject
            case.narrative = content.narrative
            case.claims = [dict(claim) for claim in content.claims]
            case.jurisdiction = dict(content.jurisdiction)
        return case

    def save_owned(
        self,
        case: CivicCase,
        *,
        identity: IdentityContext,
        execution_context: CapabilityExecutionContext | None = None,
    ) -> CivicCaseResult:
        self._validate_execution_context(execution_context, identity, action="save")
        owned = self.get_owned(case.case_id, identity=identity)
        if owned is None:
            raise LookupError("Case not found")
        self._repository.save(case, principal_id=identity.principal.principal_id)
        self._save_content(case, identity=identity)
        return CivicCaseResult(case, AuthorizationDecision.ALLOW)

    def _save_content(self, case: CivicCase, *, identity: IdentityContext) -> None:
        existing = self._content.get(case.case_id, principal_id=identity.principal.principal_id)
        self._content.save(
            case.case_id,
            CaseContent(
                subject=existing.subject if existing is not None else case.subject,
                narrative=case.narrative,
                claims=tuple(dict(claim) for claim in case.claims),
                jurisdiction=dict(case.jurisdiction),
            ),
            principal_id=identity.principal.principal_id,
        )
