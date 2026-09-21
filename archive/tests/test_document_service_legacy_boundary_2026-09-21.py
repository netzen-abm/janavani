import pytest

from src.services.document_service import generate_complaint_artifact, generate_complaint_document


@pytest.mark.parametrize("function", [generate_complaint_document, generate_complaint_artifact])
def test_legacy_document_service_fails_closed(function) -> None:
    with pytest.raises(RuntimeError, match="not an authoritative Janavani document path"):
        function("Citizen", "Address", "office-1", "Issue")
