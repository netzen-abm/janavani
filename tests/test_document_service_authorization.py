import pytest

from src.authorization.guards import AuthorizationDenied
from src.identity.context import IdentityContext
from src.identity.principal import Principal
from src.services.document_service import generate_complaint_document


def test_document_generation_denies_anonymous_request():
    context = IdentityContext(Principal("anon-1"))

    with pytest.raises(AuthorizationDenied):
        generate_complaint_document(
            context,
            user_name="Test Citizen",
            user_address="Test Address",
            office_id="1",
            issue_text="ration denied",
        )


def test_document_generation_allows_explicit_capability(monkeypatch):
    context = IdentityContext(
        Principal("user-1", capabilities=frozenset({"citizen.document.generate"}))
    )

    monkeypatch.setattr(
        "src.services.document_service.build_complaint",
        lambda **kwargs: {"complaint_id": "JVTEST"},
    )
    monkeypatch.setattr(
        "src.services.document_service.generate_pdf_from_complaint",
        lambda complaint: "PDF Generated: complaint_JVTEST.pdf",
    )

    result = generate_complaint_document(
        context,
        user_name="Test Citizen",
        user_address="Test Address",
        office_id="1",
        issue_text="ration denied",
    )

    assert result == "PDF Generated: complaint_JVTEST.pdf"
