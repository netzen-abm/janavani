import pytest

from src.platform.privacy_gateway import PrivacyViolation, assert_non_personal, sanitize_for_ai


def test_public_context_is_allowed():
    payload = sanitize_for_ai(
        purpose="authority research",
        text="Which department handles street lighting complaints?",
        context={"district": "Ernakulam"},
    )
    assert_non_personal(payload)


@pytest.mark.parametrize(
    "value",
    [
        "9876543210",
        "123456789012",
        "ABCDE1234F",
        "citizen@example.com",
    ],
)
def test_personal_data_is_blocked(value):
    with pytest.raises(PrivacyViolation):
        sanitize_for_ai(purpose="test", text=value)


def test_nested_personal_data_is_blocked():
    with pytest.raises(PrivacyViolation):
        sanitize_for_ai(purpose="test", context={"profile": {"phone": "9876543210"}})
