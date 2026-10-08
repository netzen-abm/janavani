"""Document preparation, review, and artifact HTTP routes."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import Response
from src.capabilities.document_review import DocumentReviewRequest
from src.documents.artifact_service import render_artifact_payload
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.web.civic_case_dependencies import CAPABILITY, CIVIC_ACTION, DOCUMENT_REVIEW
from src.web.civic_case_models import ArtifactRequest, DocumentPackageRequest, DocumentReviewRequestModel, serialize_draft

router = APIRouter(tags=["Civic Cases"])

@router.get("/{case_id}/document/draft")
async def build_document_draft(case_id: str, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        prepared = CIVIC_ACTION.prepare_document(case_id, identity=context)
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
async def generate_document_artifact(case_id: str, request: ArtifactRequest, context: IdentityContext = Depends(require_authenticated_identity)):
    """Render the finished document ephemerally for immediate citizen download."""
    try:
        draft = DOCUMENT_REVIEW.get_owned(request.document_id, identity=context)
        if draft is None or draft.case_id != case_id:
            raise LookupError("Document draft not found")
        payload = render_artifact_payload(draft, request.document_format)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document draft not found") from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    return Response(
        content=payload.content,
        media_type=payload.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{payload.filename}"',
            "X-Artifact-SHA256": payload.content_sha256,
            "X-Janavani-Delivery": "citizen-download-only",
            "Cache-Control": "no-store, private",
        },
    )


@router.post("/{case_id}/document/package")
async def prepare_document_package(case_id: str, request: DocumentPackageRequest, context: IdentityContext = Depends(require_authenticated_identity)):
    """Retired server-side package path; package generation must not create durable document payloads."""
    raise HTTPException(
        status_code=410,
        detail=(
            "Server-side document packages are retired. Generate and download each document through "
            "the ephemeral document endpoint; Janavani never stores or submits finished documents."
        ),
    )


