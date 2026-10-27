# Smoke tests for the canonical source package.


def test_search_and_rate():
    """Exercise the existing directory search and rating service entry points."""
    from src.services.search_directory import search_office
    from src.services.rate_office import save_rating

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
