"""In-memory provider for the external channel registry."""
from __future__ import annotations

from src.core.delivery_channel import ExternalChannel, ExternalChannelRepository


class InMemoryExternalChannelRepository(ExternalChannelRepository):
    """Deterministic repository for tests and local composition."""

    def __init__(self, channels: tuple[ExternalChannel, ...] = ()) -> None:
        self._channels = {channel.channel_id: channel for channel in channels}

    def get(self, channel_id: str) -> ExternalChannel | None:
        return self._channels.get(channel_id)

    def list_for_authority(self, authority_id: str) -> tuple[ExternalChannel, ...]:
        return tuple(
            channel
            for channel in self._channels.values()
            if channel.authority_id == authority_id
        )

    def list_for_jurisdiction(self, jurisdiction: str) -> tuple[ExternalChannel, ...]:
        return tuple(
            channel
            for channel in self._channels.values()
            if channel.jurisdiction == jurisdiction
        )
