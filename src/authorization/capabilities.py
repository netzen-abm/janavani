"""Canonical capability identifiers and access classification."""

# Public capabilities contain only genuinely public information/actions.
PUBLIC_CAPABILITIES = frozenset({"public.search_office", "public.complaint_status"})

# Citizen capabilities are not anonymous by default. They require an explicit
# grant through the authorization policy (authentication may be provided by
# any supported identity adapter).
DOCUMENT_GENERATE = "citizen.document.generate"
DOCUMENT_TRANSMIT = "citizen.document.transmit"
CITIZEN_COMPLAINT_START = "citizen.complaint.start"
CITIZEN_RATING_SUBMIT = "citizen.rating.submit"

PROTECTED_CAPABILITIES = frozenset(
    {
        DOCUMENT_GENERATE,
        DOCUMENT_TRANSMIT,
        CITIZEN_COMPLAINT_START,
        CITIZEN_RATING_SUBMIT,
    }
)
