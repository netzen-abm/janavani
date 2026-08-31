"""Shared boundary for consequential external transmissions."""

from dataclasses import dataclass
from typing import FrozenSet

from src.authorization.consent import ConsentRecord, require_consent
from src.authorization.endpoint import authorize_capability
from src.identity.context import IdentityContext


TRANSMIT_CAPABILITY = "citizen.document.transmit"
TRANSMIT_ACTION = "external.document.transmission"


@dataclass(frozen=True)
class TransmissionAuthorization:
    """Evidence that a transmission passed authorization and consent gates."""

    consent: ConsentRecord
    destination: str


def authorize_transmission(
    context: IdentityContext,
    destination: str,
    *,
    granted_consent_actions: FrozenSet[str] = frozenset(),
) -> TransmissionAuthorization:
    """Authorize an external transmission; never perform the transmission.

    This function is intentionally a policy gate. The caller remains
    responsible for performing the actual network operation after receiving
    this authorization evidence.
    """
    authorize_capability(context, TRANSMIT_CAPABILITY)
    consent = require_consent(
        context,
        TRANSMIT_ACTION,
        consented_actions=granted_consent_actions,
    )
    return TransmissionAuthorization(consent=consent, destination=destination)
