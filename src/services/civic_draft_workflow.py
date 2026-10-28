"""Shared deterministic civic-draft preview and optional AI-improvement workflow.

The workflow is used by independent surfaces. It never saves a draft or sends it
to an authority. Model output is a proposal; the citizen remains the editor.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from src.access.remote_civic_drafting_policy import identity_for_explicit_remote_drafting
from src.capabilities.letter_body import compose_template_body
from src.capabilities.letter_drafting import LetterDraftRequest
from src.documents.template_catalogue import get_template
from src.identity.context import IdentityContext
from src.identity.principal import AuthenticationMethod, IdentityMode
from src.services.legal_agent import JanavaniLegalAgent


_MAX_ISSUE_CHARS = 5_000
_MAX_DRAFT_CHARS = 8_000
@dataclass(frozen=True, slots=True)
class CivicDraftPreviewRequest:
    """Citizen-controlled inputs for a non-persistent document preview."""

    template_id: str
    issue: str
    subject: str = ""
    existing_draft: str = ""
    jurisdiction: str = ""
    requested_documents: tuple[str, ...] = field(default_factory=tuple)
    part_i_interrogatories: tuple[str, ...] = field(default_factory=tuple)
    requested_conditions: tuple[str, ...] = field(default_factory=tuple)
    remedies_reserved: tuple[str, ...] = field(default_factory=tuple)
    response_period: str | None = None
    deadline_date: str | None = None


class CivicDraftPreviewWorkflow:
    """Compose a citizen-reviewed preview using the canonical template catalogue."""

    def __init__(self, agent: JanavaniLegalAgent | None = None) -> None:
        self._agent = agent or JanavaniLegalAgent()

    def preview(
        self,
        request: CivicDraftPreviewRequest,
        *,
        identity: IdentityContext | None = None,
        use_ai: bool = False,
        remote_processing_consent: bool = False,
        location_code: str | None = None,
    ) -> dict[str, Any]:
        issue = request.issue.strip()
        existing = request.existing_draft.strip()
        if not issue:
            raise ValueError("Describe the civic issue before drafting")
        if len(issue) > _MAX_ISSUE_CHARS or len(existing) > _MAX_DRAFT_CHARS:
            raise ValueError("Issue or existing draft exceeds the allowed length")
        for name, count, size in (
            ("requested_documents", 12, 800), ("part_i_interrogatories", 12, 800),
            ("requested_conditions", 12, 800), ("remedies_reserved", 8, 500),
        ):
            values = getattr(request, name)
            if len(values) > count or any(
                not isinstance(v, str) or not v.strip() or len(v) > size for v in values
            ):
                raise ValueError(f"{name} exceeds drafting limits")
        template = get_template(request.template_id)
        subject = request.subject.strip() or self._default_subject(issue)
        if len(subject) > 200:
            raise ValueError("Subject must be 200 characters or fewer")
        if template.template_id == "rti.records":
            if not request.jurisdiction.strip():
                raise ValueError("Select the public authority or jurisdiction for an RTI draft")
            if not request.requested_documents or any(
                not item.strip() for item in request.requested_documents
            ):
                raise ValueError("Specify the existing records requested in the RTI draft")

        required_values = {
            "subject": subject,
            "issue": issue,
            "jurisdiction": request.jurisdiction.strip(),
            "requested_documents": request.requested_documents,
        }
        missing = [
            name for name in template.required_fields
            if not required_values.get(name)
        ]
        if missing:
            raise ValueError("Template requires: " + ", ".join(missing))

        proposal = existing
        interrogatories = request.part_i_interrogatories
        conditions = request.requested_conditions
        remedies = request.remedies_reserved
        ai_used = False
        ai_status = "not_requested"
        message = "Template preview created locally; it has not been saved or submitted."

        if use_ai and not remote_processing_consent:
            ai_status = "consent_required"
            message = (
                "No remote AI call was made. Explicit consent is required before the "
                "issue and any pasted draft are sent to the configured AI provider."
            )
        elif use_ai:
            if (
                identity is None
                or identity.principal.identity_mode is not IdentityMode.AUTHENTICATED
                or identity.principal.authentication_method is AuthenticationMethod.NONE
            ):
                ai_status = "identity_required"
                message = "A verified identity is required for remote AI drafting."
            else:
                identity = identity_for_explicit_remote_drafting(
                    identity, explicit_consent=remote_processing_consent
                )
                ai_input = issue
                if existing:
                    ai_input += "\n\nCitizen-provided draft to improve (preserve its purpose and facts):\n" + existing
                scope = self._agent.remote_consent_scope(location_code=location_code)
                generated = self._agent.draft_legal_document(
                    ai_input,
                    location_code=location_code,
                    consent_scope=scope,
                    identity=identity,
                    document_type=template.document_type,
                )
                ai_used = bool(generated.get("ai_used"))
                ai_status = str(generated.get("status", "degraded"))
                if ai_status == "available" and isinstance(generated.get("structured_draft"), dict):
                    structured = generated["structured_draft"]
                    proposal = str(structured.get("proposal_or_notice") or proposal)
                    interrogatories = tuple(structured.get("part_i_interrogatories") or interrogatories)
                    conditions = tuple(structured.get("requested_conditions") or conditions)
                    remedies = tuple(structured.get("remedies_reserved") or remedies)
                    if not request.subject.strip():
                        subject = str(structured.get("subject") or subject)[:200]
                    ai_used = bool(generated.get("ai_used"))
                    message = (
                        "AI suggestions were generated for review. Verify every fact and legal "
                        "reference; Janavani has not saved or submitted this draft."
                    )
                else:
                    message = str(generated.get(
                        "message", "AI did not produce validated suggestions; the local template remains available."
                    ))

        draft_request = LetterDraftRequest(
            subject=subject,
            issue=issue,
            proposal_or_notice=proposal,
            part_i_interrogatories=tuple(interrogatories),
            requested_conditions=tuple(conditions),
            requested_documents=tuple(item.strip() for item in request.requested_documents),
            remedies_reserved=tuple(remedies),
            response_period=request.response_period,
            deadline_date=request.deadline_date,
            jurisdiction=request.jurisdiction.strip() or None,
            document_type=template.document_type,
            language=template.language,
            template_id=template.template_id,
            template_version=template.version,
        )
        return {
            "status": "preview",
            "template_id": template.template_id,
            "template_version": template.version,
            "document_type": template.document_type,
            "subject": subject,
            "draft_body": compose_template_body(draft_request, template),
            "ai_used": ai_used,
            "ai_status": ai_status,
            "message": message,
            "persistence": "not_persisted",
            "submission": "not_submitted",
        }

    @staticmethod
    def _default_subject(issue: str) -> str:
        line = next((value.strip() for value in issue.splitlines() if value.strip()), issue)
        return " ".join(line.split())[:200] or "Citizen civic issue"
