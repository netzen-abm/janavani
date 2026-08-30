from datetime import datetime, timedelta, timezone

from src.capabilities.capability_consent import (
    CapabilityConsentEvaluator,
    CapabilityPolicy,
    ConsentDecision,
    ConsentGrant,
    DataClass,
    DataRequirement,
    ProcessingMode,
)


def _policy(**kwargs):
    return CapabilityPolicy.create(
        "JNV-AI-DRAFT",
        "draft civic document",
        [
            DataRequirement("issue_type", DataClass.NON_SENSITIVE),
            DataRequirement("sanitized_facts", DataClass.NON_SENSITIVE),
        ],
        provider_id="local-ai",
        processing_mode=ProcessingMode.LOCAL,
        consent_required=True,
        **kwargs,
    )


def _grant(**kwargs):
    return ConsentGrant(
        capability_id="JNV-AI-DRAFT",
        purpose="draft civic document",
        approved_fields=frozenset({"issue_type", "sanitized_facts"}),
        provider_id="local-ai",
        processing_mode=ProcessingMode.LOCAL,
        **kwargs,
    )


def test_missing_grant_requires_consent():
    result = CapabilityConsentEvaluator().evaluate(_policy(), None)
    assert result.decision is ConsentDecision.REQUIRED


def test_matching_grant_is_accepted():
    result = CapabilityConsentEvaluator().evaluate(_policy(), _grant())
    assert result.decision is ConsentDecision.GRANTED
    assert result.allowed_fields == {"issue_type", "sanitized_facts"}


def test_grant_cannot_widen_capability_scope():
    policy = _policy()
    grant = ConsentGrant(
        capability_id=policy.capability_id,
        purpose=policy.purpose,
        approved_fields=frozenset({"issue_type", "sanitized_facts", "name", "phone"}),
        provider_id=policy.provider_id,
        processing_mode=policy.processing_mode,
    )
    result = CapabilityConsentEvaluator().evaluate(policy, grant)
    assert result.decision is ConsentDecision.GRANTED
    assert result.allowed_fields == {"issue_type", "sanitized_facts"}
    assert "name" not in result.allowed_fields


def test_wrong_provider_is_rejected():
    grant = _grant(provider_id="cloud-ai")
    result = CapabilityConsentEvaluator().evaluate(_policy(), grant)
    assert result.decision is ConsentDecision.SCOPE_MISMATCH


def test_partial_field_scope_is_denied():
    grant = _grant(approved_fields=frozenset({"issue_type"}))
    result = CapabilityConsentEvaluator().evaluate(_policy(), grant)
    assert result.decision is ConsentDecision.DENIED
    assert result.missing_fields == {"sanitized_facts"}


def test_expired_grant_is_rejected():
    now = datetime.now(timezone.utc)
    grant = _grant(expires_at=now - timedelta(seconds=1))
    result = CapabilityConsentEvaluator().evaluate(_policy(), grant, now=now)
    assert result.decision is ConsentDecision.EXPIRED
