import pytest

from src.core.civic_case import CaseType, CivicCase
from src.storage.repositories.civic_case_repository import InMemoryCivicCaseRepository


def test_repository_requires_policy_and_enforces_case_access():
    repo = InMemoryCivicCaseRepository()
    case = CivicCase("case-1", CaseType.COMPLAINT, "Road", "Broken road")

    with pytest.raises(PermissionError):
        repo.create(case, access_policy_ref="")

    repo.create(case, access_policy_ref="case-private")
    assert repo.get("case-1", access_policy_ref="case-private") is case

    with pytest.raises(PermissionError):
        repo.get("case-1", access_policy_ref="other-policy")


def test_repository_does_not_allow_duplicate_case_ids():
    repo = InMemoryCivicCaseRepository()
    case = CivicCase("case-1", CaseType.COMPLAINT, "Road", "Broken road")
    repo.create(case, access_policy_ref="case-private")

    with pytest.raises(ValueError):
        repo.create(case, access_policy_ref="case-private")
