from src.core.emergency_directory import ServiceCategory, get_public_service_destination, list_public_service_destinations


def test_112_is_in_public_service_registry() -> None:
    item = get_public_service_destination("india:national-emergency:112")
    assert item is not None
    assert item.number == "112"
    assert item.category is ServiceCategory.EMERGENCY


def test_registry_contains_source_backed_core_entries() -> None:
    numbers = {item.number for item in list_public_service_destinations()}
    assert {"112", "102", "100", "101", "1930", "1915", "181", "1098", "14567", "139", "1947"} <= numbers
