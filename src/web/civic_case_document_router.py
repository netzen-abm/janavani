"""Document preparation, review, and artifact HTTP routes."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from src.capabilities.document_review import DocumentReviewRequest
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.web.civic_case_dependencies import CIVIC_ACTION, DOCUMENT_REVIEW
from src.web.civic_case_models import ArtifactRequest, DocumentReviewRequestModel, serialize_draft

router = APIRouter(tags=["Civic Cases"])

@router.get("/{case_id}/document/draft")
async def build_document_draft(case_id: str, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        prepared = CIVIC_ACTION.build_document(case_id, identity=context)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return serialize_draft(prepared.draft, case_id=prepared.case_id, submission="not_submitted")

@router.post("/{case_id}/document/review")
async def review_document(request: DocumentReviewRequestModel, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        draft = DOCUMENT_REVIEW.edit(
            DocumentReviewRequest(document_id=request.document_id, subject=request.subject, body=request.body, reason=request.reason),
            identity=context,
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document draft not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    return serialize_draft(draft, case_id=draft.case_id, submission="not_submitted")

@router.post("/{case_id}/document/artifact")
async def generate_document_artifact(case_id: str, request: ArtifactRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        artifact = CIVIC_ACTION.generate_reviewable_artifact(
            request.document_id, identity=context, case_id=case_id, document_format=request.document_format
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document draft not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return {
        "case_id": case_id, "document_id": request.document_id,
        "artifact_id": artifact.reference.artifact_id,
        "format": request.document_format.value, "submission": "not_submitted",
    }
