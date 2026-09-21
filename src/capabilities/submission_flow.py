"""Submission orchestration kept outside the public capability façade."""
from __future__ import annotations

from dataclasses import replace
from uuid import uuid4

from src.access.authorization import AuthorizationDecision
from src.access.consequential import ConsequentialDecision
from src.capabilities.submission_delivery import deliver
from src.capabilities.submission_contract import SubmissionRequest
from src.core.submission import SubmissionRecord
from src.storage.repositories.submission_case_transaction import (
    SubmissionCaseConcurrencyError,
)


def submit(capability, request: SubmissionRequest, *, identity, explicit_user_approval,
           execution_context=None):
    capability._validate_execution_context(
        execution_context, identity, action="case:submit", resource_id=request.case_id
    )
    case = capability._cases.get_owned(request.case_id, identity=identity)
    if case is None:
        raise LookupError("Case not found")
    if request.document_id not in case.document_refs:
        raise ValueError("Document is not attached to the case")
    if not request.destination_ref.strip():
        raise ValueError("A submission destination is required")

    key = request.idempotency_key or (
        execution_context.idempotency_key if execution_context is not None else None
    ) or f"subreq_{uuid4().hex}"
    decision = capability._consequential_submission_decision(
        identity=identity, case_id=case.case_id,
        consent_scope=request.consent_scope,
        explicit_user_approval=explicit_user_approval,
        execution_context=execution_context, idempotency_key=key,
    )
    if decision is not ConsequentialDecision.ALLOW:
        messages = {
            ConsequentialDecision.DENY: "Identity is not authorized to submit this case",
            ConsequentialDecision.CONSENT_REQUIRED: "Explicit consent is required for submission",
            ConsequentialDecision.REQUIRE_APPROVAL: "Explicit user approval is required for submission",
        }
        raise PermissionError(messages.get(decision, "Submission was denied"))

    proposed = SubmissionRecord.new(
        submission_id=f"sub_{uuid4().hex}", case_id=case.case_id,
        destination_ref=request.destination_ref, document_ref=request.document_id,
        channel=request.source_channel or "shared", idempotency_key=key,
    )
    submission = _reserve(capability, proposed, request, identity, case)
    if submission.state in {"submitted", "acknowledged"}:
        final = capability._cases.get_owned(request.case_id, identity=identity)
        if final is None:
            raise LookupError("Case not found after idempotent replay")
        return final
    submission = _mark_submitting(capability, submission, request, identity, execution_context)

    external_ref, evidence_id, notes = deliver(capability, submission, request, case)
    submitted = capability._mark_submitted(submission, external_ref, request, identity, execution_context)
    if evidence_id:
        fresh_case = capability._cases.get_owned(request.case_id, identity=identity)
        if fresh_case is None:
            raise LookupError("Case not found before acknowledgement")
        capability._acknowledge(
            case=fresh_case, submission=submitted, evidence_id=evidence_id,
            identity=identity, source_channel=request.source_channel,
            notes=notes, execution_context=execution_context,
        )
    final_case = capability._cases.get_owned(request.case_id, identity=identity)
    if final_case is None:
        raise LookupError("Case not found after submission")
    return final_case


def _reserve(capability, proposed, request, identity, case):
    if capability._atomic is not None and capability._submissions is not None:
        existing = capability._submissions.get_by_idempotency_key(
            proposed.idempotency_key
        )
        if existing is None:
            result = capability._atomic_case_mutation(
                submission=replace(proposed, state="submitting"),
                expected_submission_version=0, case=case,
                expected_case_version=case.version, action="case:begin_submission",
                identity=identity, source_channel=request.source_channel,
            )
            if result.idempotent_replay:
                existing = capability._submissions.get_by_idempotency_key(
                    proposed.idempotency_key
                )
                if existing is None:
                    raise SubmissionCaseConcurrencyError(
                        "Idempotent submission reservation is missing"
                    )
                return _replay_or_raise(capability, existing, request, identity)
            return replace(proposed, state="submitting")
        return _existing(capability, existing, request, identity)

    existing, replay = capability._reserve(proposed)
    if replay:
        return _replay_or_raise(capability, existing, request, identity)
    return existing


def _existing(capability, submission, request, identity):
    if submission.state in {"submitted", "acknowledged"}:
        final = capability._cases.get_owned(request.case_id, identity=identity)
        if final is None:
            raise LookupError("Case not found after idempotent replay")
        return submission
    if submission.state == "unknown":
        raise RuntimeError("Submission already exists for this idempotency key and requires reconciliation")
    if submission.state not in {"failed", "submitting"}:
        raise RuntimeError(f"Submission is not retryable: {submission.state}")
    return submission


def _replay_or_raise(capability, submission, request, identity):
    return _existing(capability, submission, request, identity)


def _mark_submitting(capability, submission, request, identity, execution_context):
    if submission.state == "created":
        updated = capability._with_submitting(submission)
        capability._save(updated, expected_version=submission.version)
        if capability._atomic is None:
            capability._cases.transition(
                request.case_id, action="case:begin_submission", identity=identity,
                source_channel=request.source_channel,
                execution_context=capability._child_case_context(
                    execution_context, identity, request.case_id, "case:begin_submission"
                ),
            )
        return updated
    if submission.state == "failed":
        updated = capability._with_submitting(submission)
        capability._save(updated, expected_version=submission.version)
        return updated
    if submission.state != "submitting":
        raise RuntimeError(f"Unsupported submission state: {submission.state}")
    return submission
