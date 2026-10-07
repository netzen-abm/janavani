"""Document preparation, review, and artifact HTTP routes."""
from __future__ import annotations
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from src.capabilities.document_review import DocumentReviewRequest
from src.identity.context import IdentityContext
from src.identity.http_assertion import require_authenticated_identity
from src.web.civic_case_dependencies import CIVIC_ACTION, CIVIC_ACTION_VERTICAL_SLICE, DOCUMENT_REVIEW
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
async def generate_document_artifact(case_id: str, request: ArtifactRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        artifact = CIVIC_ACTION_VERTICAL_SLICE.generate_artifact(
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


@router.post("/{case_id}/document/package")
async def prepare_document_package(case_id: str, request: DocumentPackageRequest, context: IdentityContext = Depends(require_authenticated_identity)) -> dict[str, object]:
    try:
        package = CIVIC_ACTION_VERTICAL_SLICE.prepare_delivery_package(
            case_id, identity=context, document_type=request.document_type,
            formats=tuple(format.value for format in request.formats),
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Case not found") from exc
    except ValueError as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return {
        "case_id": case_id,
        "document_type": package.document_type,
        "delivery": "citizen_download_and_self_send",
        "submission": "never_submitted_by_janavani",
        "from_address": "citizen_must_fill_before_sending",
        "to": {"name": package.draft.to.name, "address": package.draft.to.address, "email": package.draft.to.email},
        "cc": [{"name": p.name, "address": p.address, "email": p.email, "role": p.role} for p in package.draft.cc],
        "artifacts": [
            {"artifact_id": artifact.reference.artifact_id, "format": artifact.format.value,
             "download": f"/civic/cases/{case_id}/document/artifact/{artifact.reference.artifact_id}/download"}
            for artifact in package.artifacts
        ],
    }

@router.get("/{case_id}/document/artifact/{artifact_id}/download")
async def download_document_artifact(case_id: str, artifact_id: str, context: IdentityContext = Depends(require_authenticated_identity)):
    try:
        artifact, stream = CIVIC_ACTION_VERTICAL_SLICE._documents.open_artifact(
            artifact_id, case_id=case_id, identity=context
        )
    except LookupError as exc:
        raise HTTPException(status_code=404, detail="Document artifact not found") from exc
    media_type = "application/pdf" if artifact.format == "pdf" else "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    filename = f"{artifact.document_id}.{artifact.format}"
    return StreamingResponse(stream, media_type=media_type, headers={"Content-Disposition": f'attachment; filename="{filename}"'})
