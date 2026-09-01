# tests/test_smoke.py

def test_search_and_rate():
    """Basic smoke test: verify search_office and save_rating return strings and do not crash.

    This test intentionally avoids PDF generation (weasyprint) to keep CI lightweight.
    """
    from src.services.search_directory import search_office
    from src.services.rate_office import save_rating

    # search_office should always return a string (message or results)
    out = search_office("ration", "Kochi")
    assert isinstance(out, str)

    # save_rating should return a success message string (or an explanatory error)
    res = save_rating(office_id="3", rating=3, issue="smoke test issue", user_phone="000")
    assert isinstance(res, str)
    assert res.startswith("Saved.") or res.startswith("Failed") or res.startswith("Invalid")
