from src.core.capability_router import CapabilityRouter
from src.core.contracts.access_surface import CapabilityRequest, CapabilityResponse


class FakeCapability:
    def handle(self, request):
        return CapabilityResponse(
            request_id=request.request_id,
            ok=True,
            status="completed",
            data={"capability": request.capability_id, "action": request.action},
        )


def test_router_dispatches_normalized_request():
    router = CapabilityRouter()
    router.register("case.create", FakeCapability())
    result = router.dispatch(CapabilityRequest("r1", "case.create", "create", source="telegram"))
    assert result.ok is True
    assert result.data["capability"] == "case.create"


def test_router_rejects_unknown_capability():
    result = CapabilityRouter().dispatch(CapabilityRequest("r2", "unknown", "run"))
    assert result.ok is False
    assert result.error_code == "unknown_capability"


def test_same_contract_is_independent_of_channel():
    router = CapabilityRouter()
    router.register("case.create", FakeCapability())
    telegram = router.dispatch(CapabilityRequest("r3", "case.create", "create", source="telegram"))
    webapp = router.dispatch(CapabilityRequest("r4", "case.create", "create", source="webapp"))
    miniapp = router.dispatch(CapabilityRequest("r5", "case.create", "create", source="telegram_miniapp"))
    assert all(result.ok for result in (telegram, webapp, miniapp))
