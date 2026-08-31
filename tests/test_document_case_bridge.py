import pytest

from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.document_case_bridge import SharedDocumentCaseBridge
from src.core.contracts.case_action_graph import CivicAction
from src.core.contracts.document_delivery import CivicDocument, DocumentAddress, DocumentFormat, DocumentStatus


def document(status=DocumentStatus.USER_REVIEW):
    return CivicDocument("doc-1", "case-1", "complaint", DocumentFormat.PDF, DocumentAddress("Authority", "Address"), content="content", status=status)


def test_document_creates_delivery_action():
    graph = SharedCaseActionGraph()
    previous = graph.add_action("case-1", CivicAction.COMPLAINT, status="completed")
    link = SharedDocumentCaseBridge().add_document_action(graph, document=document(), previous_action_id=previous.action_id)
    assert graph.get_action(link.action_id).action == CivicAction.DOCUMENT_DELIVERY
    assert link.status == DocumentStatus.USER_REVIEW


def test_document_status_can_sync():
    graph = SharedCaseActionGraph()
    link = SharedDocumentCaseBridge().add_document_action(graph, document=document())
    updated = SharedDocumentCaseBridge().sync_status(graph, link=link, document=document(DocumentStatus.DELIVERED))
    assert updated.status == DocumentStatus.DELIVERED
    assert graph.get_action(link.action_id).status == "delivered"


def test_cross_case_link_rejected():
    graph = SharedCaseActionGraph()
    previous = graph.add_action("case-2", CivicAction.COMPLAINT, status="completed")
    with pytest.raises(ValueError):
        SharedDocumentCaseBridge().add_document_action(graph, document=document(), previous_action_id=previous.action_id)
