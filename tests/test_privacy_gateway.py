import pytest

from src.capabilities.privacy_gateway import PrivacyGateway


def test_gateway_allows_only_sanitized_public_context():
    decision = PrivacyGateway().authorize_ai(
        {
            "task": "draft a complaint",
            "issue_type": "road maintenance",
            "jurisdiction": "Kochi",
            "public_facts": ["Road maintenance is handled by the responsible local authority."],
            "document_purpose": "complaint",
            "language": "en",
        },
        user_opted_in=True,
    )
    assert decision.allowed is True
    assert "name" not in decision.context


def test_gateway_rejects_identity_fields():
    decision = PrivacyGateway().authorize_ai(
        {"task": "draft", "name": "Citizen", "issue_type": "road"},
        user_opted_in=True,
    )
    assert decision.allowed is False
    assert decision.reason == "unexpected_or_private_fields"


def test_gateway_rejects_evidence_like_objects():
    decision = PrivacyGateway().authorize_ai(
        {"task": "analyze", "evidence": {"filename": "photo.jpg"}},
        user_opted_in=True,
    )
    assert decision.allowed is False


def test_gateway_blocks_without_user_opt_in():
    decision = PrivacyGateway().authorize_ai(
        {"task": "draft", "issue_type": "road"},
        user_opted_in=False,
    )
    assert decision.allowed is False
    assert decision.reason == "ai_not_enabled_by_user"
