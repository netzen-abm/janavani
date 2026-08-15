from typing import Dict, Any

# Localized regional administrative metadata map profile structures.
# Keeps LLM completions locked strictly to valid administrative tiers by default.
SOUTH_INDIAN_MUNICIPAL_PROFILES: Dict[str, Dict[str, Any]] = {
    "KL-TVM-01": {
        "state": "Kerala",
        "district": "Thiruvananthapuram",
        "local_body_type": "Municipal Corporation",
        "administrative_head_designation": "The Secretary, Thiruvananthapuram Municipal Corporation",
        "official_vernacular_language": "Malayalam",
        "primary_postal_address": "Vikas Bhavan P.O., Thiruvananthapuram, Kerala - 695033",
        "mandatory_rti_statute_reference": "Section 6(1) of the Right to Information Act, 2005"
    },
    "KA-BLR-02": {
        "state": "Karnataka",
        "district": "Bengaluru Urban",
        "local_body_type": "Bruhat Bengaluru Mahanagara Palike (BBMP)",
        "administrative_head_designation": "The Chief Commissioner, BBMP Central Office",
        "official_vernacular_language": "Kannada",
        "primary_postal_address": "Hudson Circle, Bengaluru, Karnataka - 560002",
        "mandatory_rti_statute_reference": "Section 6(1) of the Right to Information Act, 2005"
    },
    "TN-CHN-03": {
        "state": "Tamil Nadu",
        "district": "Chennai",
        "local_body_type": "Greater Chennai Corporation",
        "administrative_head_designation": "The Regional Joint Commissioner, Greater Chennai Corporation",
        "official_vernacular_language": "Tamil",
        "primary_postal_address": "Ripon Building, EVR Salai, Chennai, Tamil Nadu - 600003",
        "mandatory_rti_statute_reference": "Section 6(1) of the Right to Information Act, 2005"
    }
}

def fetch_profile_by_code(location_code: str) -> Dict[str, Any]:
    """Retrieves target structural data mapping profiles securely from local memory matrices."""
    return SOUTH_INDIAN_MUNICIPAL_PROFILES.get(
        location_code, 
        {
            "state": "Unknown",
            "district": "Unknown",
            "local_body_type": "Fallback Administrative Officer",
            "administrative_head_designation": "The Competent Public Authority",
            "official_vernacular_language": "English",
            "primary_postal_address": "District Collectorate Headquarters",
            "mandatory_rti_statute_reference": "Section 6(1) of the Right to Information Act, 2005"
        }
    )
