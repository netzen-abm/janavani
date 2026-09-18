from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EmergencyActionKind(str, Enum):
    CALL = "CALL"
    MANUAL_CONTACT = "MANUAL_CONTACT"


@dataclass(frozen=True)
class EmergencyDestination:
    ref: str
    display_name: str
    number: str
    scope: str
    services: tuple[str, ...]
    action_kinds: tuple[EmergencyActionKind, ...]
    source_url: str
    source_label: str


INDIA_NATIONAL_EMERGENCY_112 = EmergencyDestination(
    ref="india:national-emergency:112",
    display_name="National Emergency Response Support System",
    number="112",
    scope="india",
    services=("POLICE", "FIRE", "HEALTH"),
    action_kinds=(EmergencyActionKind.CALL,),
    source_url="https://www.india.gov.in/directory/helpline",
    source_label="National Portal of India — Helpline",
)


def get_emergency_destination(ref: str) -> EmergencyDestination | None:
    if ref == INDIA_NATIONAL_EMERGENCY_112.ref:
        return INDIA_NATIONAL_EMERGENCY_112
    return None
