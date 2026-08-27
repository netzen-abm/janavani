def test_canonical_kernel_exports_are_importable():
    from src.application import CivicActionService
    from src.domain import (
        AuthorityReference,
        Case,
        CivicActionWorkflow,
        Evidence,
        Submission,
    )
    from src.storage.repositories.protocol import CaseRepository

    assert Case
    assert Evidence
    assert AuthorityReference
    assert Submission
    assert CivicActionWorkflow
    assert CivicActionService
    assert CaseRepository
