"""Privacy boundary primitives for JanaVani.

This module intentionally contains policy-enforcement primitives rather than a
central user-data store. It provides a small, dependency-free vocabulary that
other capabilities can use to classify data and to construct minimized
capability requests.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import FrozenSet, Mapping


class DataClass(str, Enum):
    """Storage/processing sensitivity class."""

    PUBLIC = "public"
    OPERATIONAL = "operational"
    USER_PRIVATE = "user_private"
    SENSITIVE = "sensitive"


class Capability(str, Enum):
    """Independent execution boundaries recognized by the ecosystem."""

    WEB = "web"
    ANDROID = "android"
    IOS = "ios"
    DAPP = "dapp"
    NOSTR = "nostr"
    NYM = "nym"
    RETICULUM = "reticulum"
    FREENET = "freenet"
    TELEGRAM = "telegram"
    TELEGRAM_MINI_APP = "telegram_mini_app"
    WHATSAPP = "whatsapp"
    MESSENGER = "messenger"
    AI = "ai"
    AGENTIC_AI = "agentic_ai"
    SLM = "slm"
    RAG = "rag"
    VLM = "vlm"
    LAM = "lam"
    MOE = "moe"
    MLM = "mlm"
    SAM = "sam"
    OCR = "ocr"
    COMPUTER_VISION = "computer_vision"
    BLOCKCHAIN = "blockchain"
    ZKP = "zkp"


@dataclass(frozen=True)
class CapabilityRequest:
    """The minimum contract needed before protected data leaves a device."""

    capability: Capability
    fields: FrozenSet[str]
    user_authorized: bool = False
    encrypted: bool = False

    def validate(self) -> None:
        """Reject requests that violate the privacy boundary."""
        if not self.user_authorized:
            raise PermissionError("Protected capability request is not user-authorized")
        if not self.encrypted:
            raise PermissionError("Protected capability request must be encrypted")


SENSITIVE_FIELD_NAMES: FrozenSet[str] = frozenset(
    {
        "name",
        "postal_address",
        "phone",
        "email",
        "government_id",
        "identity_document",
        "biometric",
        "precise_location",
        "location_history",
        "private_key",
        "wallet_seed",
        "private_message",
        "private_attachment",
        "private_prompt",
        "private_ai_output",
    }
)


class PrivacyBoundary:
    """Pure functions used by independent capabilities to enforce minimization."""

    @staticmethod
    def classify_field(field_name: str) -> DataClass:
        normalized = field_name.strip().lower()
        if normalized in SENSITIVE_FIELD_NAMES:
            return DataClass.SENSITIVE
        if normalized in {"draft", "complaint", "grievance", "evidence", "attachment"}:
            return DataClass.USER_PRIVATE
        if normalized in {"request_id", "capability", "created_at", "status", "error_code"}:
            return DataClass.OPERATIONAL
        return DataClass.PUBLIC

    @classmethod
    def minimize(cls, payload: Mapping[str, object], allowed_fields: FrozenSet[str]) -> dict[str, object]:
        """Return only explicitly allowed fields; never broaden a capability scope."""
        return {key: value for key, value in payload.items() if key in allowed_fields}

    @staticmethod
    def assert_no_sensitive_keys(payload: Mapping[str, object]) -> None:
        """Guard operational/backend payloads against obvious sensitive fields."""
        leaked = [key for key in payload if PrivacyBoundary.classify_field(key) is DataClass.SENSITIVE]
        if leaked:
            raise ValueError(f"Sensitive fields cannot enter an unclassified backend payload: {sorted(leaked)}")
