import pytest

from src.core.capability_registry import CapabilityDescriptor, default_registry


def test_default_registry_is_channel_shared():
    registry = default_registry()
    assert {"telegram", "webapp", "telegram_miniapp"}.issubset(
        registry.get("case").consumers
    )
    assert "document" in registry.ids()


def test_ai_is_user_controlled():
    ai = default_registry().get("ai")
    assert ai.requires_ai is True
    assert ai.ai_user_controlled is True


def test_document_exposes_user_selected_formats():
    document = default_registry().get("document")
    assert document.output_formats == frozenset({"pdf", "document"})


def test_duplicate_capability_ids_are_rejected():
    registry = default_registry()
    with pytest.raises(ValueError):
        registry.register(
            CapabilityDescriptor("case", "Duplicate", "x", frozenset({"webapp"}))
        )


def test_ai_cannot_be_registered_as_implicitly_mandatory():
    with pytest.raises(ValueError):
        CapabilityDescriptor(
            "bad-ai", "Bad AI", "x", frozenset({"webapp"}), requires_ai=True,
            ai_user_controlled=False
        )
