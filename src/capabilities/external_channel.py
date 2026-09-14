"""Shared read-only capability for external channel discovery.

This boundary exposes verified channel metadata to access surfaces without
allowing a surface to own routing or delivery semantics.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.core.delivery_channel import (
    ExternalChannel,
    ExternalChannelRepository,
    require_verified_channel,
)


@dataclass(frozen=True)
class ExternalChannelQuery:
    channel_id: str | None = None
    authority_id: str | None = None
    jurisdiction: str | None = None


class ExternalChannelCapability:
    """Canonical channel discovery capability."""

    def __init__(self, repository: ExternalChannelRepository) -> None:
        self._repository = repository

    def get_verified(self, channel_id: str) -> ExternalChannel:
        return require_verified_channel(self._repository, channel_id)

    def discover(self, query: ExternalChannelQuery | None = None) -> tuple[ExternalChannel, ...]:
        if query is None:
            raise ValueError("A channel_id, authority_id, or jurisdiction is required")
        if query.channel_id is not None:
            return (self.get_verified(query.channel_id),)
        if query.authority_id is not None:
            channels = self._repository.list_for_authority(query.authority_id)
        elif query.jurisdiction is not None:
            channels = self._repository.list_for_jurisdiction(query.jurisdiction)
        else:
            raise ValueError("A channel_id, authority_id, or jurisdiction is required")
        return tuple(channel for channel in channels if channel.is_usable)
