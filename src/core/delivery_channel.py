"""Provider-neutral contracts for verified external civic-action channels.

A channel is an external destination available to a citizen case.  The
registry records provenance and verification metadata; it does not perform
delivery, routing, authorization, or submission.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class ExternalChannel:
    """Immutable, source-backed description of an external channel."""

    channel_id: str
    authority_id: str
    channel_type: str
    destination_ref: str
    jurisdiction: str
    source_ref: str
    verified_at: str
    verification_status: str = "VERIFIED"
    notes: str | None = None

    def __post_init__(self) -> None:
        for field_name in (
            "channel_id",
            "authority_id",
            "channel_type",
            "destination_ref",
            "jurisdiction",
            "source_ref",
            "verified_at",
        ):
            if not getattr(self, field_name).strip():
                raise ValueError(f"{field_name} is required")
        if self.verification_status not in {"VERIFIED", "UNVERIFIED", "REVOKED"}:
            raise ValueError("verification_status must be VERIFIED, UNVERIFIED, or REVOKED")

    @property
    def is_usable(self) -> bool:
        """Only currently verified channels are eligible for selection."""
        return self.verification_status == "VERIFIED"


class ExternalChannelRepository(Protocol):
    """Provider-neutral read contract for external channel metadata."""

    def get(self, channel_id: str) -> ExternalChannel | None:
        """Return one channel by canonical identifier."""
        ...

    def list_for_authority(self, authority_id: str) -> tuple[ExternalChannel, ...]:
        """Return channels belonging to one authority."""
        ...

    def list_for_jurisdiction(self, jurisdiction: str) -> tuple[ExternalChannel, ...]:
        """Return channels applicable to one jurisdiction."""
        ...


def require_verified_channel(
    repository: ExternalChannelRepository,
    channel_id: str,
) -> ExternalChannel:
    """Fail closed unless the requested external channel is verified."""
    channel = repository.get(channel_id)
    if channel is None:
        raise LookupError("External channel was not found")
    if not channel.is_usable:
        raise PermissionError("External channel is not currently verified")
    return channel
