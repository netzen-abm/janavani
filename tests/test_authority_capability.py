from src.domain.authority import Authority, AuthorityQuery
from src.services.authority_capability import AuthorityCapability


class Provider:
    name = "test"

    def __init__(self, authorities):
        self.authorities = authorities

    def find(self, query):
        return self.authorities


def test_authority_resolution_preserves_verification_state():
    authority = Authority(
        id="authority-1",
        name="Test Municipal Office",
        jurisdiction="Ward 1",
        verification_state="verified",
    )
    matches = AuthorityCapability([Provider([authority])]).resolve(
        AuthorityQuery(issue="road repair", location="Ward 1")
    )
    assert len(matches) == 1
    assert matches[0].verified is True
    assert matches[0].confidence == 1.0


def test_unverified_authority_is_not_presented_as_verified():
    authority = Authority(
        id="authority-2",
        name="Candidate Office",
        jurisdiction="Ward 2",
        verification_state="unverified",
    )
    matches = AuthorityCapability([Provider([authority])]).resolve(
        AuthorityQuery(issue="road repair")
    )
    assert matches[0].verified is False
    assert matches[0].confidence < 1.0


def test_duplicate_authorities_are_deduplicated_across_providers():
    authority = Authority(id="authority-3", name="Shared Office")
    capability = AuthorityCapability([Provider([authority]), Provider([authority])])
    matches = capability.resolve(AuthorityQuery(issue="office"))
    assert [m.authority.id for m in matches] == ["authority-3"]
