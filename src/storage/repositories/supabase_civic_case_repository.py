"""Supabase adapter for the privacy-aware civic case repository.

This adapter stores civic metadata and policy references only. The Supabase
service role must remain server-side; browser/DApp clients must not receive it.
"""

from __future__ import annotations

from typing import Any

from src.core.civic_case import CaseStatus, CaseType, CivicCase
from src.storage.repositories.civic_case_repository import CivicCaseRepository


class SupabaseCivicCaseRepository(CivicCaseRepository):
    def __init__(self, client: Any) -> None:
        self.client = client

    def create(self, case: CivicCase, *, access_policy_ref: str) -> CivicCase:
        self._require_policy(access_policy_ref)
        payload = self._case_payload(case, access_policy_ref)
        result = self.client.table("civic_cases").insert(payload).execute()
        if not result.data:
            raise RuntimeError("Supabase did not return the created civic case")
        return case

    def get(self, case_id: str, *, access_policy_ref: str) -> CivicCase | None:
        self._require_policy(access_policy_ref)
        result = (
            self.client.table("civic_cases")
            .select("*")
            .eq("case_id", case_id)
            .eq("access_policy_ref", access_policy_ref)
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None
        return self._case_from_row(result.data)

    def save(self, case: CivicCase, *, access_policy_ref: str) -> CivicCase:
        self._require_policy(access_policy_ref)
        result = (
            self.client.table("civic_cases")
            .update(self._case_payload(case, access_policy_ref))
            .eq("case_id", case.case_id)
            .eq("access_policy_ref", access_policy_ref)
            .execute()
        if not result.data:
            raise PermissionError("Case not found or access policy mismatch")
        return case

    def _case_payload(self, case: CivicCase, policy: str) -> dict[str, object]:
        return {
            "case_id": case.case_id,
            "case_type": case.case_type.value,
            "subject": case.subject,
            "narrative": case.narrative,
            "created_by_ref": case.created_by,
            "related_office_id": case.related_office_id,
            "evidence_refs": case.evidence_refs,
            "document_refs": case.document_refs,
            "consent_refs": case.consent_refs,
            "status": case.status.value,
            "access_policy_ref": policy,
        }

    @staticmethod
    def _case_from_row(row: dict[str, Any]) -> CivicCase:
        return CivicCase(
            case_id=row["case_id"],
            case_type=CaseType(row["case_type"]),
            subject=row["subject"],
            narrative=row["narrative"],
            created_by=row.get("created_by_ref"),
            related_office_id=row.get("related_office_id"),
            evidence_refs=list(row.get("evidence_refs") or []),
            document_refs=list(row.get("document_refs") or []),
            consent_refs=list(row.get("consent_refs") or []),
            status=CaseStatus(row.get("status", CaseStatus.DRAFT.value)),
        )

    @staticmethod
    def _require_policy(policy: str) -> None:
        if not policy.strip():
            raise PermissionError("An access policy reference is required")
