"""Legacy text-search adapter over the canonical authority contract."""
from __future__ import annotations

from src.core.authority import AuthorityRepository
from src.services.authority_service import find_authorities


def search_office(
    query: str,
    city: str = "Kochi",
    *,
    repository: AuthorityRepository | None = None,
) -> str:
    """Preserve the historical text response while using AuthorityRepository."""
    if not query or not query.strip():
        return "Invalid search query. Provide the department or office type."

    authorities = find_authorities(
        query,
        city,
        repository=repository,
        limit=5,
    )
    if not authorities:
        return f"No {query.strip()} found in {city.strip()}."

    output = f"Found {len(authorities)} {query.strip()}(s) in {city.strip()}:\n\n"
    for authority in authorities:
        contact = authority.primary_contact
        output += f"ID: {authority.authority_id}\n"
        output += f"Name: {authority.name}\n"
        output += f"Address: {contact.address if contact else ''}\n"
        output += f"Officer: {contact.role if contact else ''}\n"
        output += f"Email: {contact.email if contact else ''}\n"
        output += "---\n"

    output += "\nReply with the ID to file a complaint."
    return output
