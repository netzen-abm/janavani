"""Channel-neutral case action graph contracts."""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CivicAction(str, Enum):
    COMPLAINT = "complaint"
    RTI = "rti"
    FOLLOW_UP = "follow_up"
    ESCALATION = "escalation"
    EVIDENCE_SUPPORT = "evidence_support"
    PARTY_IN_PERSON_SUPPORT = "party_in_person_support"
    DOCUMENT_DELIVERY = "document_delivery"
    CLOSED = "closed"


class ActionRelation(str, Enum):
    FOLLOWS = "follows"
    PARALLEL = "parallel"
    TRIGGERED_BY = "triggered_by"
    SUPPORTS = "supports"


@dataclass(frozen=True)
class CaseActionNode:
    action_id: str
    case_id: str
    action: CivicAction
    status: str = "planned"


@dataclass(frozen=True)
class CaseActionEdge:
    from_action_id: str
    to_action_id: str
    relation: ActionRelation
    trigger: Optional[str] = None


@dataclass(frozen=True)
class CaseActionGraph:
    case_id: str
    nodes: tuple[CaseActionNode, ...]
    edges: tuple[CaseActionEdge, ...]
