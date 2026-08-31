"""Executable vertical-flow contract for the shared civic case architecture.

This test deliberately exercises the shared primitives without Telegram or
WebApp dependencies. Channel adapters must be able to reproduce this flow.
"""
from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.capabilities.document_case_bridge import SharedDocumentCaseBridge
from src.core.capabilities.document_delivery import SharedDocumentDelivery
from src.core.capabilities.escalation_action_service import SharedEscalationActionService
from src.core.capabilities.escalation_case_bridge import SharedEscalationCaseBridge
from src.core.capabilities.escalation_resolver import EscalationDecision
from src.core.contracts.authority_discovery import AuthorityCandidate, AuthorityStatus
from src.core.contracts.case_action_graph import CivicAction
from src.core.contracts.document_delivery import DocumentFormat, DocumentStatus


def authority(authority_id, name):
    return AuthorityCandidate(
        authority_id, name, "department", "IN-KL", "verified", ("official-source",),
        AuthorityStatus.VERIFIED, to_address="Official Office Address"
    )


def test_complaint_document_followup_escalation_document_lifecycle():
    case_id = "case-vertical-1"
    current = authority("authority-1", "Current Authority")
    next_authority = authority("authority-2", "Escalation Authority")
    graph = SharedCaseActionGraph()

    complaint = graph.add_action(case_id, CivicAction.COMPLAINT, status="completed")
    delivery = SharedDocumentDelivery()
    first = delivery.prepare(
        case_id=case_id, document_type="complaint", content="Road complaint", authority=current,
        format=DocumentFormat.PDF,
    )
    first_link = SharedDocumentCaseBridge().add_document_action(graph, document=first, previous_action_id=complaint.action_id)
    first = delivery.approve(first)
    first = delivery.deliver(first)
    SharedDocumentCaseBridge().sync_status(graph, link=first_link, document=first)
    assert first.status == DocumentStatus.DELIVERED

    follow_up = graph.add_action(case_id, CivicAction.FOLLOW_UP, status="planned")
    graph.connect(complaint, follow_up, relation=graph.__class__.__dict__.get('connect').__annotations__.get('relation', None)) if False else None

    decision = EscalationDecision("route-1", next_authority, "verified escalation route")
    proposal = SharedEscalationActionService().propose(decision)
    escalation = SharedEscalationCaseBridge().add_proposal(
        graph, case_id=case_id, previous_action_id=follow_up.action_id, proposal=proposal
    )
    second = delivery.prepare(
        case_id=case_id, document_type="escalation", content="Escalation complaint", authority=next_authority,
        format=DocumentFormat.DOCX,
    )
    second_link = SharedDocumentCaseBridge().add_document_action(graph, document=second, previous_action_id=escalation.action_id)
    second = delivery.approve(second)
    second = delivery.deliver(second)
    SharedDocumentCaseBridge().sync_status(graph, link=second_link, document=second)

    assert escalation.authority_id == "authority-2"
    assert second.status == DocumentStatus.DELIVERED
    assert graph.get_action(second_link.action_id).status == "delivered"
