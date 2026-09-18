from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ServiceCategory(str, Enum):
    EMERGENCY = "EMERGENCY"
    POLICE = "POLICE"
    FIRE = "FIRE"
    MEDICAL = "MEDICAL"
    CYBERCRIME = "CYBERCRIME"
    WOMEN = "WOMEN"
    CHILDREN = "CHILDREN"
    SENIOR_CITIZENS = "SENIOR_CITIZENS"
    CONSUMER = "CONSUMER"
    RAILWAY = "RAILWAY"
    IDENTITY = "IDENTITY"


class ContactAction(str, Enum):
    CALL = "CALL"
    MANUAL_CONTACT = "MANUAL_CONTACT"


@dataclass(frozen=True)
class PublicServiceDestination:
    ref: str
    name: str
    number: str
    category: ServiceCategory
    scope: str
    action: ContactAction
    source_url: str
    source_label: str
    review_required: bool = True


INDIA_PUBLIC_SERVICE_DESTINATIONS: tuple[PublicServiceDestination, ...] = (
    PublicServiceDestination("india:national-emergency:112", "Integrated Emergency Response Support System", "112", ServiceCategory.EMERGENCY, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:national-ambulance:102", "National Ambulance Service", "102", ServiceCategory.MEDICAL, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:police:100", "Police Helpline", "100", ServiceCategory.POLICE, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:fire:101", "Fire Helpline", "101", ServiceCategory.FIRE, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:cybercrime:1930", "Cyber Crime Helpline", "1930", ServiceCategory.CYBERCRIME, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:consumer:1915", "National Consumer Helpline", "1915", ServiceCategory.CONSUMER, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:women:181", "Women Helpline", "181", ServiceCategory.WOMEN, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:children:1098", "Child Helpline", "1098", ServiceCategory.CHILDREN, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:senior-citizens:14567", "Senior Citizens Helpline", "14567", ServiceCategory.SENIOR_CITIZENS, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:railway:139", "Railway Security/Medical Assistance Helpline", "139", ServiceCategory.RAILWAY, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
    PublicServiceDestination("india:uidai:1947", "UIDAI Toll Free", "1947", ServiceCategory.IDENTITY, "india", ContactAction.CALL, "https://www.india.gov.in/directory/helpline", "National Portal of India — Helpline"),
)


def get_public_service_destination(ref: str) -> PublicServiceDestination | None:
    return next((item for item in INDIA_PUBLIC_SERVICE_DESTINATIONS if item.ref == ref), None)


def list_public_service_destinations() -> tuple[PublicServiceDestination, ...]:
    return INDIA_PUBLIC_SERVICE_DESTINATIONS
