"""Shared bridge between citizen-reviewed documents and case actions."""
from __future__ import annotations

from dataclasses import dataclass

from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.contracts.case_action_graph import ActionRelation, CivicAction
from src.core.contracts.document_delivery import CivicDocument, DocumentStatus


@dataclass(frozen=True)
class DocumentCaseLink:
    action_id: str
    document_id: str
    case_id: str
    status: DocumentStatus


class SharedDocumentCaseBridge:
    def add_document_action(
        self,
        graph: SharedCaseActionGraph,
        *,
        document: CivicDocument,
        previous_action_id: str | None = None,
    ) -> DocumentCaseLink:
        if not document.case_id.strip():
            raise ValueError("document case_id is required")
        action = graph.add_action(document.case_id, CivicAction.DOCUMENT_DELIVERY, status=document.status.value)
        if previous_action_id is not None:
            previous = graph.get_action(previous_action_id)
            if previous.case_id != document.case_id:
                raise ValueError("previous action does not belong to document case")
            graph.connect(previous, action, ActionRelation.FOLLOWS)
        return DocumentCaseLink(action.action_id, document.document_id, document.case_id, document.status)

    def sync_status(self, graph: SharedCaseActionGraph, *, link: DocumentCaseLink, document: CivicDocument) -> DocumentCaseLink:
        if document.case_id != link.case_id or document.document_id != link.document_id:
            raise ValueError("document does not match case link")
        graph.transition(link.action_id, document.status.value)
        return DocumentCaseLink(link.action_id, link.document_id, link.case_id, document.status)
