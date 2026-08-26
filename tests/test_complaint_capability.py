from src.platform.contracts import CapabilityRequest
from src.capabilities.complaint import ComplaintCapability


def test_complaint_capability_is_channel_neutral():
    result = ComplaintCapability().handle(
        CapabilityRequest(
            capability="complaint",
            request_id="test-request-1",
            actor_id=None,
            metadata={"channel": "telegram"},
            payload={"text": "Street light is not working"},
        )
    )

    assert result.status == "completed"
    assert result.capability == "complaint"
    assert result.data["issue"] == "Street light is not working"


def test_complaint_capability_rejects_empty_text():
    result = ComplaintCapability().handle(
        CapabilityRequest(
            capability="complaint",
            request_id="test-request-2",
            actor_id=None,
            metadata={"channel": "web"},
            payload={"text": ""},
        )
    )

    assert result.status == "rejected"
