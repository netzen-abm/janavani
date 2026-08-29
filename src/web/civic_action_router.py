"""Web boundary for the shared Civic Action capability."""
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.domain.case import CaseCreate
from src.services.civic_action_capability import CivicActionCapability
from src.services.evidence_capability import EvidenceItem

router = APIRouter(prefix="/api/v1/civic-actions", tags=["Civic Action"])
_capability = CivicActionCapability()


class CreateCivicActionRequest(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=10000)
    location: str | None = Field(default=None, max_length=500)
    category: str | None = Field(default=None, max_length=120)
    evidence: list[EvidenceItem] = Field(default_factory=list)


@router.post("", status_code=201)
def create_civic_action(payload: CreateCivicActionRequest):
    return _capability.create(
        CaseCreate(
            title=payload.title,
            description=payload.description,
            location=payload.location,
            category=payload.category,
        ),
        payload.evidence,
    )
