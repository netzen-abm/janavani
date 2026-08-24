"""Repository boundary for civic cases.

The adapter stores only the civic case contract and its policy references. Raw
identity, evidence bytes, and credentials stay outside this repository boundary.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from src.core.civic_case import CivicCase


class CivicCaseRepository(Protocol):
    def create(self, case: CivicCase, *, access_policy_ref: str) -> CivicCase: ...
    def get(self, case_id: str, *, access_policy_ref: str) -> CivicCase | None: ...
    def save(self, case: CivicCase, *, access_policy_ref: str) -> CivicCase: ...


@dataclass
class InMemoryCivicCaseRepository:
    """Deterministic adapter for tests/local development only."""

    _cases: dict[str, CivicCase]
    _policies: dict[str, str]

    def __init__(self) -> None:
        self._cases = {}
        self._policies = {}

    def create(self, case: CivicCase, *, access_policy_ref: str) -> CivicCase:
        if not access_policy_ref.strip():
            raise PermissionError("An access policy reference is required")
        if case.case_id in self._cases:
            raise ValueError("Case already exists")
        self._cases[case.case_id] = case
        self._policies[case.case_id] = access_policy_ref
        return case

    def get(self, case_id: str, *, access_policy_ref: str) -> CivicCase | None:
        if not self._authorized(case_id, access_policy_ref):
            raise PermissionError("Case access denied")
        return self._cases.get(case_id)

    def save(self, case: CivicCase, *, access_policy_ref: str) -> CivicCase:
        if not self._authorized(case.case_id, access_policy_ref):
            raise PermissionError("Case access denied")
        self._cases[case.case_id] = case
        return case

    def _authorized(self, case_id: str, access_policy_ref: str) -> bool:
        return bool(access_policy_ref.strip()) and self._policies.get(case_id) == access_policy_ref
