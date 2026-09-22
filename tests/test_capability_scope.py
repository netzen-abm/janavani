from src.access.capability_scope import (
    CapabilityDataScope,
    CapabilityDataScopePolicy,
    CapabilityScopeDecision,
    DataClassification,
    DataRequirement,
)


def _policy():
    return CapabilityDataScopePolicy(
        capability_id="JNV-AI-RAG",
        requirements=(
            DataRequirement("question", DataClassification.NON_SENSITIVE),
            DataRequirement("location", DataClassification.PERSONAL),
        ),
    )


def test_unknown_field_is_denied():
    assert _policy().evaluate(
        purpose="civic_research",
        requested_fields=frozenset({"question", "secret"}),
        provider="local",
        processing_mode="local",
    ) is CapabilityScopeDecision.DENY


def test_non_sensitive_minimum_data_can_proceed_without_consent():
    assert _policy().evaluate(
        purpose="civic_research",
        requested_fields=frozenset({"question"}),
        provider="local",
        processing_mode="local",
    ) is CapabilityScopeDecision.ALLOW


def test_personal_data_requires_exact_scoped_consent():
    scope=CapabilityDataScope(
        capability_id="JNV-AI-RAG",
        purpose="civic_research",
        approved_fields=frozenset({"location"}),
        provider="local",
        processing_mode="local",
    )
    assert _policy().evaluate(
        purpose="civic_research",
        requested_fields=frozenset({"location"}),
        provider="local",
        processing_mode="local",
        consent_scope=scope,
    ) is CapabilityScopeDecision.ALLOW


def test_consent_cannot_cross_provider_or_processing_mode():
    scope=CapabilityDataScope(
        capability_id="JNV-AI-RAG",
        purpose="civic_research",
        approved_fields=frozenset({"location"}),
        provider="local",
        processing_mode="local",
    )
    assert _policy().evaluate(
        purpose="civic_research",
        requested_fields=frozenset({"location"}),
        provider="cloud",
        processing_mode="remote",
        consent_scope=scope,
    ) is CapabilityScopeDecision.REQUIRE_CONSENT
