import pytest

from src.platform.privacy_gateway import PrivacyViolation
from src.services.ai_context import build_non_personal_ai_context


def test_builds_allow_listed_context():
    payload = build_non_personal_ai_context(
        purpose="draft public-facing civic guidance",
        task_type="document_draft",
        document_type="complaint",
        language="en",
        jurisdiction_level="district",
        public_authority_name="District Administration",
        public_source_urls=["https://example.gov.in/source"],
        public_facts=["The authority publishes a grievance procedure."],
        requested_output="structured draft",
    )
    assert payload.data_classification == "non_personal"
    assert payload.context["task_type"] == "document_draft"
    assert "public_authority_name" in payload.context


def test_personal_data_is_rejected():
    with pytest.raises(PrivacyViolation):
        build_non_personal_ai_context(
            purpose="draft",
            task_type="document_draft",
            public_facts=["Contact me at citizen@example.com"],
        )
