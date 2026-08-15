from typing import Dict, Any

# Regional translation heading configurations for official petitions.
# Helps ensure that printed documents match traditional administrative styles.
VERNACULAR_LEGISLATIVE_HEADERS: Dict[str, Dict[str, str]] = {
    "Kerala": {
        "salutation": "ബഹുമാനപ്പെട്ട നിയമസഭാ സെക്രട്ടറി സമക്ഷം,", # To the Respected Legislative Secretary
        "subject_prefix": "വിഷയം:", # Subject
        "reference_prefix": "സൂചന:", # Reference
        "prayer_prefix": "ആവശ്യപ്പെടുന്നു:" # Prayers/Demands
    },
    "Karnataka": {
        "salutation": "ಗೌರವಾನ್ವಿತ ವಿಧಾನಸಭಾ ಕಾರ್ಯದರ್ಶಿಯವರಿಗೆ,", # To the Honorable Legislative Secretary
        "subject_prefix": "ವಿಷಯ:",
        "reference_prefix": "ಉಲ್ಲೇಖ:",
        "prayer_prefix": "ಮನವಿ:"
    },
    "Tamil Nadu": {
        "salutation": "மதிப்பிற்குரிய சட்டமன்ற செயலாளர் அவர்களுக்கு,", # To the Respected Legislative Secretary
        "subject_prefix": "பொருள்:",
        "reference_prefix": "பார்வை:",
        "prayer_prefix": "கோரிக்கை:"
    },
    "Assam": {
        "salutation": "মাননীয় বিধানসভা সচিব মহোদয় সমীপেষু,", # To the Respected Legislative Secretary
        "subject_prefix": "বিষয়:",
        "reference_prefix": "প্ৰসংগ:",
        "prayer_prefix": "প্ৰাৰ্থনা:"
    }
}

def fetch_localized_header_map(state_name: str) -> Dict[str, str]:
    """Retrieves localized text markers to build traditional petition headings."""
    return VERNACULAR_LEGISLATIVE_HEADERS.get(
        state_name, 
        {
            "salutation": "To, The Competent Legislative Authority,",
            "subject_prefix": "SUBJECT:",
            "reference_prefix": "REFERENCE:",
            "prayer_prefix": "PRAYER:"
        }
    )
