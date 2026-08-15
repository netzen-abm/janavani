import pytest
from src.core.vernacular_headers import fetch_localized_header_map

def test_vernacular_mapping_values():
    """Verifies that the configuration engine fetches accurate regional headers for listed states."""
    kerala_headers = fetch_localized_header_map("Kerala")
    assert kerala_headers["subject_prefix"] == "വിഷയം:"
    
    assam_headers = fetch_localized_header_map("Assam")
    assert assam_headers["subject_prefix"] == "বিষয়:"

def test_vernacular_mapping_unmapped_fallback():
    """Confirms that the configuration script falls back gracefully to English formatting if a state is missing."""
    fallback_headers = fetch_localized_header_map("Unmapped-State-Zone")
    assert fallback_headers["subject_prefix"] == "SUBJECT:"
    assert "Competent Legislative Authority" in fallback_headers["salutation"]
