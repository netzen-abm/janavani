import pytest

from src.access.capability_scope import CapabilityDataScope
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode, Principal
from src.services.civic_draft_workflow import (
    CivicDraftPreviewRequest,
    CivicDraftPreviewWorkflow,
)


class FakeAgent:
    provider_id = "openrouter"

    def __init__(self, result=None):
        self.calls = []
        self.result = result or {
            "status": "available",
            "ai_used": True,
            "structured_draft": {
                "subject": "AI suggested subject",
                "proposal_or_notice": "Please inspect and provide a written response.",
                "part_i_interrogatories": ["Which office is responsible?"],
                "requested_conditions": ["Please provide a status update."],
                "remedies_reserved": [],
            },
        }

    def remote_consent_scope(self, *, location_code=None):
        return CapabilityDataScope(
            capability_id="civic:ai-draft",
            purpose="civic_document_drafting",
            approved_fields=frozenset({"citizen_issue"}),
            provider=self.provider_id,
            processing_mode="remote_model",
        )

    def draft_legal_document(self, issue, **kwargs):
        self.calls.append((issue, kwargs))
        return self.result


def _identity(*capabilities):
    return IdentityContext(
        principal=Principal(
            principal_id="draft-preview-citizen",
            identity_mode=IdentityMode.AUTHENTICATED,
            interface="test",
            authentication_method=AuthenticationMethod.PASSKEY,
            capabilities=frozenset(capabilities),
        )
    )


def test_complaint_preview_is_deterministic_and_never_persisted():
    workflow = CivicDraftPreviewWorkflow(agent=FakeAgent())
    result = workflow.preview(CivicDraftPreviewRequest(
        template_id="complaint.general",
        issue="The public streetlight has not worked for three nights.",
    ))

    assert result["template_version"] == 1
    assert result["ai_used"] is False
    assert result["persistence"] == "not_persisted"
    assert result["submission"] == "not_submitted"
    assert "The public streetlight has not worked for three nights." in result["draft_body"]


def test_rti_requires_jurisdiction_and_existing_records():
    workflow = CivicDraftPreviewWorkflow(agent=FakeAgent())
    request = CivicDraftPreviewRequest(
        template_id="rti.records",
        issue="Please provide records about a road repair.",
    )
    try:
        workflow.preview(request)
        assert False, "RTI template must require jurisdiction and requested records"
    except ValueError as exc:
        assert "jurisdiction" in str(exc).lower()

    request = CivicDraftPreviewRequest(
        template_id="rti.records",
        issue="Please provide records about a road repair.",
        jurisdiction="Kerala State public authority",
        requested_documents=("Copies of existing work orders",),
    )
    result = workflow.preview(request)
    assert "Existing records requested" in result["draft_body"]
    assert "not a request for a newly created explanation" in result["draft_body"]


def test_ai_is_not_called_without_explicit_remote_processing_consent():
    agent = FakeAgent()
    result = CivicDraftPreviewWorkflow(agent=agent).preview(
        CivicDraftPreviewRequest(
            template_id="complaint.general",
            issue="The road needs repair.",
        ),
        identity=_identity("civic:ai-draft"),
        use_ai=True,
        remote_processing_consent=False,
    )

    assert agent.calls == []
    assert result["ai_status"] == "consent_required"
    assert result["ai_used"] is False
    assert result["persistence"] == "not_persisted"


def test_ai_preview_fails_closed_until_raw_narrative_minimization_is_available():
    agent = FakeAgent()
    identity = _identity("case:write")
    private_issue = "The affected citizen is Asha Example at 12 Example Road."
    private_draft = "Please contact me at asha@example.test about this matter."
    result = CivicDraftPreviewWorkflow(agent=agent).preview(
        CivicDraftPreviewRequest(
            template_id="complaint.general",
            issue=private_issue,
            existing_draft=private_draft,
        ),
        identity=identity,
        use_ai=True,
        remote_processing_consent=True,
    )

    # Explicit consent and identity do not bypass the missing minimization boundary.
    assert agent.calls == []
    assert result["ai_status"] == "privacy_boundary_required"
    assert result["ai_used"] is False
    assert "No remote AI provider was called" in result["message"]
    assert private_issue in result["draft_body"]
    assert private_draft in result["draft_body"]
    assert not identity.principal.has_capability("civic:ai-draft")
    assert result["persistence"] == "not_persisted"



def test_remote_ai_without_identity_never_calls_provider_and_keeps_deterministic_preview():
    agent = FakeAgent()
    result = CivicDraftPreviewWorkflow(agent=agent).preview(
        CivicDraftPreviewRequest(
            template_id="complaint.general",
            issue="The drain is blocked.",
        ),
        use_ai=True,
        remote_processing_consent=True,
    )
    assert agent.calls == []
    assert result["ai_status"] == "identity_required"
    assert result["ai_used"] is False
    assert "The drain is blocked." in result["draft_body"]


def test_unknown_template_fails_closed():
    workflow = CivicDraftPreviewWorkflow(agent=FakeAgent())
    try:
        workflow.preview(CivicDraftPreviewRequest(
            template_id="not-approved",
            issue="An issue exists.",
        ))
        assert False, "Unknown template must not be guessed"
    except LookupError:
        pass


def test_preview_rejects_oversized_or_blank_record_fields():
    workflow = CivicDraftPreviewWorkflow(agent=FakeAgent())
    with pytest.raises(ValueError, match="requested_documents exceeds drafting limits"):
        workflow.preview(CivicDraftPreviewRequest(
            template_id="rti.records",
            issue="Please provide records.",
            jurisdiction="Kerala State public authority",
            requested_documents=("x" * 801,),
        ))
    with pytest.raises(ValueError, match="requested_conditions exceeds drafting limits"):
        workflow.preview(CivicDraftPreviewRequest(
            template_id="complaint.general",
            issue="Please review the issue.",
            requested_conditions=(" ",),
        ))


def test_explicit_opt_in_does_not_grant_ai_capability_to_anonymous_identity():
    agent = FakeAgent()
    anonymous = IdentityContext(principal=Principal(
        principal_id="anonymous-caller",
        interface="webapp",
        capabilities=frozenset({"civic:ai-draft"}),
    ))
    result = CivicDraftPreviewWorkflow(agent=agent).preview(
        CivicDraftPreviewRequest(
            template_id="complaint.general",
            issue="The road surface is damaged.",
        ),
        identity=anonymous,
        use_ai=True,
        remote_processing_consent=True,
    )

    assert agent.calls == []
    assert result["ai_status"] == "identity_required"
    assert result["ai_used"] is False


def test_administrative_evidence_demand_requires_jurisdiction_and_uses_saved_defaults():
    workflow = CivicDraftPreviewWorkflow(agent=FakeAgent())
    with pytest.raises(ValueError, match="Template requires: jurisdiction"):
        workflow.preview(CivicDraftPreviewRequest(
            template_id="administrative.evidence-demand",
            issue="The municipal notice requests a recurring sanitation levy.",
        ))

    result = workflow.preview(CivicDraftPreviewRequest(
        template_id="administrative.evidence-demand",
        issue="The municipal notice requests a recurring sanitation levy.",
        jurisdiction="Kerala municipal authority",
        requested_documents=("A copy of the specific demand notice",),
    ))

    body = result["draft_body"]
    assert result["template_id"] == "administrative.evidence-demand"
    assert result["template_version"] == 1
    assert "Foundational and constitutional questions" in body
    assert "Documents and records requested" in body
    assert "Requested response period: [Insert a requested period" in body
    assert "Requested date: [Insert a date if appropriate" in body
    assert "certified copies in the form prescribed" in body
    assert "An affidavit is requested only where lawful and appropriate" in body
    assert "Date: [Insert date of writing]" in body
    assert "A copy of the specific demand notice" in body
    assert "Kerala municipal authority" in body
    assert "Non-response alone is not asserted here to constitute agreement" in body
    assert "self-executing instrument" not in body
    assert result["persistence"] == "not_persisted"
    assert result["submission"] == "not_submitted"
