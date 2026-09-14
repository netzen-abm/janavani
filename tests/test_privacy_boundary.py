import pytest

from src.core.privacy_boundary import (
    Capability,
    CapabilityRequest,
    DataClass,
    PrivacyBoundary,
)


def test_sensitive_fields_are_classified_as_sensitive() -> None:
    for field in ("email", "phone", "postal_address", "private_key", "identity_document"):
        assert PrivacyBoundary.classify_field(field) is DataClass.SENSITIVE


def test_user_private_content_is_not_classified_as_public() -> None:
    for field in ("draft", "complaint", "grievance", "evidence", "attachment"):
        assert PrivacyBoundary.classify_field(field) is DataClass.USER_PRIVATE


def test_minimization_never_adds_unrequested_fields() -> None:
    payload = {
        "request_id": "r-1",
        "status": "ready",
        "email": "citizen@example.invalid",
        "complaint": "private complaint",
    }
    minimized = PrivacyBoundary.minimize(payload, frozenset({"request_id", "status"}))
    assert minimized == {"request_id": "r-1", "status": "ready"}
    assert "email" not in minimized
    assert "complaint" not in minimized


def test_backend_payload_guard_rejects_sensitive_fields() -> None:
    with pytest.raises(ValueError):
        PrivacyBoundary.assert_no_sensitive_keys({"status": "ready", "email": "citizen@example.invalid"})


def test_protected_capability_requires_explicit_authorization_and_encryption() -> None:
    with pytest.raises(PermissionError):
        CapabilityRequest(Capability.AI, frozenset({"complaint"}), user_authorized=False, encrypted=True).validate()

    with pytest.raises(PermissionError):
        CapabilityRequest(Capability.AI, frozenset({"complaint"}), user_authorized=True, encrypted=False).validate()


def test_protected_capability_is_valid_only_when_both_guards_are_present() -> None:
    request = CapabilityRequest(
        Capability.AI,
        frozenset({"complaint"}),
        user_authorized=True,
        encrypted=True,
    )
    request.validate()
