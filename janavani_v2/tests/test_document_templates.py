import pytest
from src.core.document_templates import get_all_available_templates, get_template_by_id

def test_template_registry_lookup_integrity():
    """Confirms that the document template engine successfully reads and formats target patterns."""
    directory = get_all_available_templates()
    
    assert len(directory) > 0
    assert "RTI_OFFICER_MISBEHAVIOR" in directory
    assert "title" in directory["RTI_OFFICER_MISBEHAVIOR"]

    # Test rendering a specific template layout
    template = get_template_by_id("RTI_OFFICER_MISBEHAVIOR")
    assert template is not None
    assert "SECTION 6(1) OF THE RIGHT TO INFORMATION ACT" in template["template_body"]
    assert "WE, THE PEOPLE OF INDIA" in template["template_body"]

def test_template_registry_invalid_lookup_fallback():
    """Verifies that the template engine returns None for unmapped template lookup requests."""
    assert get_template_by_id("INVALID_TEMPLATE_ID_XYZ") is None
