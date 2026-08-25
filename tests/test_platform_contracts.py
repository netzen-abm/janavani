from src.platform.contracts import CapabilityRequest, CapabilityResult
from src.platform.registry import CapabilityRegistry


class FakeCapability:
    capability = "documents"

    def handle(self, request: CapabilityRequest) -> CapabilityResult:
        return CapabilityResult(
            capability=self.capability,
            request_id=request.request_id,
            status="ok",
            data={"ready": True},
        )


def test_registry_resolves_shared_capability() -> None:
    registry = CapabilityRegistry()
    handler = FakeCapability()
    registry.register(handler)

    assert registry.has("DOCUMENTS")
    assert registry.get("documents") is handler
    assert registry.names() == ("documents",)


def test_request_and_result_are_channel_neutral() -> None:
    request = CapabilityRequest(
        capability="documents",
        request_id="req-1",
        payload={"type": "complaint"},
    )
    result = FakeCapability().handle(request)

    assert result.status == "ok"
    assert result.request_id == "req-1"
