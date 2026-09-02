# tests/test_smoke.py


def test_search_and_rate():
    """Verify core office search and rating calls do not crash."""
    from src.services.rate_office import save_rating
    from src.services.search_directory import search_office

    out = search_office("ration", "Kochi")
    assert isinstance(out, str)

    result = save_rating(
        office_id="3",
        rating=3,
        issue="smoke test issue",
        user_phone="000",
    )
    assert isinstance(result, str)
    assert result.startswith(("Saved.", "Failed", "Invalid"))
