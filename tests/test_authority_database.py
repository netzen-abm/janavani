from src.core.capabilities.authority_database import AuthorityDatabaseProvider, AuthorityRecord
from src.core.capabilities.issue_understanding import IssueUnderstanding
from src.core.contracts.case import VerificationStatus


class FakeRepository:
    def search(self, *, department=None, jurisdiction=None, location=None, query=None):
        return [AuthorityRecord("a1", "Verified Office", "Address", "office@gov", department, jurisdiction, True)]


def test_authority_database_provider_returns_verified_record():
    issue = IssueUnderstanding(category="road", department="local_government")
    candidates = list(AuthorityDatabaseProvider(FakeRepository()).discover(issue, jurisdiction="Kochi"))
    assert candidates[0].authority.verification == VerificationStatus.VERIFIED
    assert candidates[0].authority.authority_id == "a1"
