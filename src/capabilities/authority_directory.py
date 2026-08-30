"""Default Authority Discovery capability backed by the existing directory provider."""

from services.search_directory import search_office_records

from capabilities.authority import AuthorityCandidate, AuthorityCapability


class DirectoryAuthorityCapability(AuthorityCapability):
    """Adapt the existing directory provider to the shared capability contract."""

    def discover(self, *, query: str, jurisdiction: str | None = None):
        rows = search_office_records(query=query, location=jurisdiction)
        return [
            AuthorityCandidate(
                authority_id=str(row.get("id", "")),
                name=str(row.get("name", "")),
                authority_type=row.get("type"),
                jurisdiction=row.get("city") or jurisdiction,
                source="directory",
            )
            for row in rows
        ]
