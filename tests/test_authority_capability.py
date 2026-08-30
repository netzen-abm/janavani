from capabilities.authority import AuthorityCandidate
from capabilities.authority_directory import DirectoryAuthorityCapability


def test_authority_candidate_contract():
    candidate = AuthorityCandidate(
        authority_id="1",
        name="Example Office",
        authority_type="ration",
        jurisdiction="Kochi",
        source="directory",
    )
    assert candidate.authority_id == "1"
    assert candidate.name == "Example Office"
    assert candidate.source == "directory"


def test_directory_authority_capability_returns_candidates(monkeypatch):
    monkeypatch.setattr(
        "capabilities.authority_directory.search_office_records",
        lambda query, location=None: [
            {
                "id": "1",
                "name": "Example Office",
                "type": "ration",
                "city": "Kochi",
            }
        ],
    )

    results = DirectoryAuthorityCapability().discover(
        query="ration",
        jurisdiction="Kochi",
    )

    assert len(results) == 1
    assert results[0].authority_id == "1"
    assert results[0].name == "Example Office"
    assert results[0].jurisdiction == "Kochi"
