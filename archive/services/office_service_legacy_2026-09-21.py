"""Legacy-shaped office lookup adapter over the canonical authority contract."""
from __future__ import annotations

from src.core.authority import AuthorityRepository
from src.services.authority_service import find_authorities


def find_offices(
    department: str,
    location: str,
    *,
    repository: AuthorityRepository | None = None,
):
    """Return the historical dict shape without owning authority lookup."""
    authorities = find_authorities(
        department,
        location,
        repository=repository,
    )
    if not authorities:
        return None

    return [
        {
            "id": authority.authority_id,
            "name": authority.name,
            "type": authority.authority_type,
            "address": (
                authority.primary_contact.address
                if authority.primary_contact
                else ""
            ),
            "city": authority.jurisdiction.get("city", ""),
            "officer_role": (
                authority.primary_contact.role
                if authority.primary_contact
                else ""
            ),
            "email": (
                authority.primary_contact.email
                if authority.primary_contact
                else None
            ),
        }
        for authority in authorities
    ]
