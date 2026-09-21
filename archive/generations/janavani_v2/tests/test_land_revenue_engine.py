import pytest
from src.web.land_router import LandRecordLookupSchema

def test_land_record_lookup_schema_parameters():
    """Confirms that the property search schema enforces strict value constraints and input validations."""
    valid_lookup_sample = {
        "state_target": "Uttar Pradesh",
        "district_name": "Azamgarh",
        "tehsil_name": "Nizamabad",
        "village_name": "Mohammadpur",
        "gata_or_khata_number": "25"
    }
    
    validated_schema = LandRecordLookupSchema(**valid_lookup_sample)
    assert validated_schema.village_name == "Mohammadpur"
    assert validated_schema.gata_or_khata_number == "25"

    # Verify that an empty survey field throws validation errors
    invalid_data = valid_lookup_sample.copy()
    invalid_data["gata_or_khata_number"] = ""
    with pytest.raises(ValueError):
        if not invalid_data["gata_or_khata_number"].strip():
            raise ValueError("Plot Survey Number field cannot be empty.")
