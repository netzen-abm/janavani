import pytest
import fakeredis
import json
from src.web.volunteer_router import VolunteerRegistrationSchema

def test_volunteer_and_institutional_registration_constraints():
    """Confirms that the volunteer registration schema enforces correct data structures and input formats."""
    valid_individual_node = {
        "registration_type": "INDIVIDUAL",
        "legal_name_or_title": "Advocate Hari Prasad",
        "area_of_expertise": "Legal Defense & Labor Law",
        "contact_email": "hari.prasad@legal.org",
        "operating_district_code": "KL-TVM-01",
        "nostr_public_key": "npub1janavani789xxyz"
    }
    
    schema = VolunteerRegistrationSchema(**valid_individual_node)
    assert schema.registration_type == "INDIVIDUAL"
    assert schema.contact_email == "hari.prasad@legal.org"

    # Verify that an invalid registration classification throws validation errors
    invalid_node = valid_individual_node.copy()
    invalid_node["registration_type"] = "INVALID_CLASSIFICATION"
    with pytest.raises(ValueError):
        VolunteerRegistrationSchema(**invalid_node)
        
    # Verify that an incorrect email format is caught by validation rules
    invalid_email_node = valid_individual_node.copy()
    invalid_email_node["contact_email"] = "broken-email-string"
    with pytest.raises(ValueError):
        VolunteerRegistrationSchema(**invalid_email_node)
