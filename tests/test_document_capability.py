from src.capabilities.document import DocumentArtifact, DocumentCapability, DocumentRequest


class FakeProvider:
    name = "fake"

    def generate(self, request):
        return DocumentArtifact(
            schema_version=1,
            document_id="doc-1",
            case_id=request.case_id,
            document_type=request.document_type,
            output_format=request.output_format,
            content="generated",
            provider=self.name,
        )


def test_document_capability_routes_to_registered_provider():
    capability = DocumentCapability()
    capability.register(FakeProvider())
    result = capability.generate(DocumentRequest(case_id="case-1", document_type="complaint"))
    assert result.case_id == "case-1"
    assert result.provider == "fake"


def test_document_capability_rejects_unsupported_type():
    capability = DocumentCapability()
    capability.register(FakeProvider())
    try:
        capability.generate(DocumentRequest(case_id="case-1", document_type="unknown"))
    except ValueError as exc:
        assert "Unsupported document type" in str(exc)
    else:
        raise AssertionError("Expected unsupported document type to fail")
