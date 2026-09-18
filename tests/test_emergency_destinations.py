from src.core.emergency import EmergencyActionKind, INDIA_NATIONAL_EMERGENCY_112, get_emergency_destination


def test_india_112_is_canonical_national_emergency_destination() -> None:
    destination = get_emergency_destination("india:national-emergency:112")
    assert destination is INDIA_NATIONAL_EMERGENCY_112
    assert destination.number == "112"
    assert destination.scope == "india"
    assert set(destination.services) == {"POLICE", "FIRE", "HEALTH"}
    assert destination.action_kinds == (EmergencyActionKind.CALL,)
    assert destination.source_url == "https://www.india.gov.in/directory/helpline"


def test_unknown_emergency_destination_is_not_invented() -> None:
    assert get_emergency_destination("india:national-emergency:999") is None
