from src.platform.capability_adapter import dispatch_transport_message
from src.platform.capabilities import build_capability_registry
from src.platform.contracts import CapabilityRequest, CapabilityResult
from src.platform.registry import CapabilityRegistry
from src.platform.transport import TransportMessage


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


def test_transport_dispatch_maps_identity_and_transport_metadata() -> None:
    registry = CapabilityRegistry()
    registry.register(FakeCapability())
    message = TransportMessage(
        transport="telegram",
        message_id="msg-1",
        actor_ref="actor-1",
        text="hello",
        metadata={"locale": "kn"},
    )

    dispatched = dispatch_transport_message(message, registry, "documents")

    assert dispatched.result.status == "ok"
    assert dispatched.result.request_id == "msg-1"


def test_default_registry_contains_complaint_capability() -> None:
    registry = build_capability_registry()

    assert registry.has("complaint")
