from src.platform.analytics import validate_dimensions


def test_allows_non_identifying_aggregate_dimensions() -> None:
    result = validate_dimensions({"document_type": "complaint", "channel_type": "web"})
    assert result.ok


def test_rejects_unknown_dimension() -> None:
    result = validate_dimensions({"campaign": "spring"})
    assert not result.ok
    assert result.error_code == "DIMENSION_NOT_ALLOWED"


def test_rejects_identity_dimension() -> None:
    result = validate_dimensions({"user_id": "123"})
    assert not result.ok
    assert result.error_code == "DIMENSION_NOT_ALLOWED"
