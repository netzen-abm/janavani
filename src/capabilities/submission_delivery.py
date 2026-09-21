"""Provider-neutral delivery execution for submission."""
from __future__ import annotations

from dataclasses import replace

from src.capabilities.submission_contract import SubmissionOutcomeUnknown
from src.core.submission import SubmissionRecord
from src.delivery.contract import (
    DeliveryArtifactResolver,
    DeliveryOutcome,
    DeliveryRequest,
    DeliveryTransport,
    DeliveryTransportError,
)
from src.storage.repositories.submission_case_transaction import SubmissionCaseTransactionRepository


def deliver(capability, submission: SubmissionRecord, request, case):
    """Resolve and deliver an approved artifact, persisting outcome safely."""
    if capability._delivery_transport is not None:
        return _deliver_artifact(capability, submission, request, case)
    try:
        receipt = capability._transport.send(
            case=case,
            document_id=request.document_id,
            destination_ref=request.destination_ref,
        )
    except Exception as exc:
        failed = replace(
            submission, state="failed", error_code=type(exc).__name__,
            retry_count=submission.retry_count + 1,
            updated_at=capability._now(), version=submission.version + 1,
        )
        capability._save(failed, expected_version=submission.version)
        raise
    return receipt.acknowledgement_ref, None, receipt.notes


def _deliver_artifact(capability, submission, request, case):
    try:
        if request.artifact_id is None:
            raise ValueError("An approved artifact is required for delivery")
        assert capability._artifact_resolver is not None
        artifact = capability._artifact_resolver.resolve(
            artifact_id=request.artifact_id,
            case_id=case.case_id,
            document_id=request.document_id,
        )
    except Exception as exc:
        failed = replace(
            submission, state="failed", error_code=type(exc).__name__,
            retry_count=submission.retry_count + 1,
            updated_at=capability._now(), version=submission.version + 1,
        )
        capability._save(failed, expected_version=submission.version)
        raise
    try:
        receipt = capability._delivery_transport.deliver(DeliveryRequest(
            submission_id=submission.submission_id,
            idempotency_key=submission.idempotency_key,
            case_id=case.case_id,
            document_id=request.document_id,
            destination_ref=request.destination_ref,
            channel=request.source_channel or "shared",
            artifact=artifact,
        ))
    except DeliveryTransportError as exc:
        if exc.outcome is DeliveryOutcome.UNKNOWN:
            _mark_unknown(capability, submission)
            raise SubmissionOutcomeUnknown(
                "Delivery outcome is unknown; reconciliation is required"
            ) from exc
        _mark_failed(capability, submission, type(exc).__name__)
        raise
    except Exception as exc:
        _mark_unknown(capability, submission)
        raise SubmissionOutcomeUnknown(
            "Delivery outcome is unknown; reconciliation is required"
        ) from exc
    if receipt.outcome is DeliveryOutcome.UNKNOWN:
        _mark_unknown(capability, submission)
        raise SubmissionOutcomeUnknown(
            "Delivery outcome is unknown; reconciliation is required"
        )
    if receipt.outcome is DeliveryOutcome.FAILED:
        _mark_failed(capability, submission, "delivery_failed")
        raise RuntimeError("Delivery transport reported failure")
    return receipt.external_reference, receipt.acknowledgement_evidence_ref, receipt.notes


def _mark_unknown(capability, submission):
    unknown = replace(
        submission, state="unknown", error_code="unknown_transport_outcome",
        updated_at=capability._now(), version=submission.version + 1,
    )
    capability._save(unknown, expected_version=submission.version)


def _mark_failed(capability, submission, error_code):
    failed = replace(
        submission, state="failed", error_code=error_code,
        retry_count=submission.retry_count + 1,
        updated_at=capability._now(), version=submission.version + 1,
    )
    capability._save(failed, expected_version=submission.version)
