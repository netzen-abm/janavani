import pytest
from src.core.legislative_monitor import fetch_active_bill_profile

def test_bill_registry_golden_triangle_evaluations():
    """Verifies that the legal engine correctly identifies non-compliant bills and flags violations."""
    bill_profile = fetch_active_bill_profile("BILL-2026-KL-04")
    
    assert bill_profile is not None
    assert bill_profile["state"] == "Kerala"
    
    evaluation = bill_profile["constitutional_evaluation"]
    assert evaluation["is_compliant_with_golden_triangle"] is False
    assert "VIOLATION DETECTED" in evaluation["article_19_analysis"]
    assert "NON-COMPLIANT" in evaluation["overall_constitutional_summary"]

def test_missing_bill_code_graceful_handling():
    """Confirms that the system handles missing bill lookups cleanly without throwing exceptions."""
    assert fetch_active_bill_profile("INVALID-BILL-CODE-XYZ") is None
