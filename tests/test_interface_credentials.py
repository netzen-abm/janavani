import pytest

from src.core.interface_credentials import (
    CredentialConfigurationError,
    get_interface_credential,
)


def test_interface_credential_is_loaded_from_environment(monkeypatch):
    monkeypatch.setenv("JANAVANI_WEB_INTERFACE_TOKEN", "test-token")
    credential = get_interface_credential("JANAVANI_WEB_INTERFACE_TOKEN")
    assert credential.value == "test-token"


def test_missing_interface_credential_fails_closed(monkeypatch):
    monkeypatch.delenv("JANAVANI_WEB_INTERFACE_TOKEN", raising=False)
    with pytest.raises(CredentialConfigurationError):
        get_interface_credential("JANAVANI_WEB_INTERFACE_TOKEN")
