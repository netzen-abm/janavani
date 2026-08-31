from src.capabilities.consent_policy import (
    CapabilityPolicy,
    ConsentDecision,
    ConsentRequest,
    ConsentScope,
    DataClass,
    DataRequirement,
    evaluate_consent,
)


POLICY = CapabilityPolicy(
    capability_id="JNV-AI-DRAFT",
    requirements=(
        DataRequirement("issue_type", DataClass.NON_SENSITIVE),
        DataRequirement("sanitized_facts", DataClass.NON_SENSITIVE),
        DataRequirement("name", DataClass.PERSONAL),
    ),
)


def test_non_personal_minimum_data_is_allowed_without_consent():
    request = ConsentRequest(
        capability_id="JNV-AI-DRAFT",
        purpose="draft civic document",
        requested_data=("issue_type", "sanitized_facts"),
        provider="local",
        processing_mode="local",
    )
    assert evaluate_consent(request, POLICY) == ConsentDecision.ALLOW


def test_personal_data_requires_exact_scoped_consent():
    request = ConsentRequest(
        capability_id="JNV-AI-DRAFT",
        purpose="draft civic document",
        requested_data=("name",),
        provider="cloud",
        processing_mode="remote",
    )
    assert evaluate_consent(request, POLICY) == ConsentDecision.REQUIRE_CONSENT

    scope = ConsentScope(
        capability_id="JNV-AI-DRAFT",
        purpose="draft civic document",
        approved_data=frozenset({"name"}),
        provider="cloud",
        processing_mode="remote",
    )
    assert evaluate_consent(request, POLICY, scope) == ConsentDecision.ALLOW


def test_unknown_or_unrequested_data_is_denied():
    request = ConsentRequest(
        capability_id="JNV-AI-DRAFT",
        purpose="draft civic document",
        requested_data=("phone",),
    )
    assert evaluate_consent(request, POLICY) == ConsentDecision.DENY


def test_consequential_action_requires_explicit_scope():
    request = ConsentRequest(
        capability_id="JNV-AI-DRAFT",
        purpose="submit civic document",
        requested_data=("issue_type",),
        consequential_action=True,
    )
    assert evaluate_consent(request, POLICY) == ConsentDecision.REQUIRE_CONSENT
