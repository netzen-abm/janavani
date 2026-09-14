from src.capabilities.external_channel import ExternalChannelCapability, ExternalChannelQuery
from src.core.delivery_channel import ExternalChannel, require_verified_channel
from src.storage.repositories.external_channel import InMemoryExternalChannelRepository


def _channel(status: str = "VERIFIED") -> ExternalChannel:
    return ExternalChannel(
        channel_id="channel-bbmp-complaint",
        authority_id="authority-bbmp",
        channel_type="web",
        destination_ref="official-complaint-endpoint",
        jurisdiction="Bengaluru",
        source_ref="official-source-2026-09-14",
        verified_at="2026-09-14T00:00:00+00:00",
        verification_status=status,
    )


def test_verified_channel_is_discoverable():
    capability = ExternalChannelCapability(InMemoryExternalChannelRepository((_channel(),)))
    result = capability.discover(ExternalChannelQuery(authority_id="authority-bbmp"))
    assert result == (_channel(),)


def test_unverified_channel_is_not_discoverable():
    capability = ExternalChannelCapability(InMemoryExternalChannelRepository((_channel("UNVERIFIED"),)))
    assert capability.discover(ExternalChannelQuery(authority_id="authority-bbmp")) == ()


def test_direct_selection_fails_closed_for_unverified_channel():
    repository = InMemoryExternalChannelRepository((_channel("REVOKED"),))
    try:
        require_verified_channel(repository, "channel-bbmp-complaint")
    except PermissionError as exc:
        assert "verified" in str(exc).lower()
    else:
        raise AssertionError("revoked channel must fail closed")
