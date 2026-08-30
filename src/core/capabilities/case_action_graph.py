"""Executable, channel-neutral civic case action graph.

The graph records what has happened and what can happen next. It does not
submit actions or send documents. A transition can require an explicit trigger
or user decision; legal/procedural triggers must be supplied by verified
sources rather than hard-coded legal deadlines.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

from src.core.contracts.case_action_graph import (
    ActionRelation,
    CaseActionEdge,
    CaseActionGraph,
    CaseActionNode,
    CivicAction,
)


@dataclass(frozen=True)
class CaseActionEvent:
    action_id: str
    case_id: str
    action: CivicAction
    status: str
    trigger: Optional[str] = None


class SharedCaseActionGraph:
    def __init__(self):
        self._nodes: dict[str, CaseActionNode] = {}
        self._edges: list[CaseActionEdge] = []

    def add_action(self, case_id: str, action: CivicAction, *, status: str = "planned") -> CaseActionNode:
        if not case_id.strip():
            raise ValueError("case_id is required")
        node = CaseActionNode(f"act-{uuid4().hex[:12]}", case_id, action, status)
        self._nodes[node.action_id] = node
        return node

    def get_action(self, action_id: str) -> CaseActionNode:
        node = self._nodes.get(action_id)
        if node is None:
            raise KeyError(action_id)
        return node

    def connect(
        self,
        from_action: CaseActionNode,
        to_action: CaseActionNode,
        relation: ActionRelation,
        *,
        trigger: Optional[str] = None,
    ) -> CaseActionEdge:
        if from_action.case_id != to_action.case_id:
            raise ValueError("actions must belong to the same case")
        edge = CaseActionEdge(from_action.action_id, to_action.action_id, relation, trigger)
        self._edges.append(edge)
        return edge

    def transition(self, action_id: str, status: str) -> CaseActionNode:
        node = self.get_action(action_id)
        updated = CaseActionNode(node.action_id, node.case_id, node.action, status)
        self._nodes[action_id] = updated
        return updated

    def graph(self, case_id: str) -> CaseActionGraph:
        nodes = tuple(node for node in self._nodes.values() if node.case_id == case_id)
        node_ids = {node.action_id for node in nodes}
        edges = tuple(edge for edge in self._edges if edge.from_action_id in node_ids)
        return CaseActionGraph(case_id, nodes, edges)

    def next_actions(self, case_id: str) -> tuple[CaseActionNode, ...]:
        graph = self.graph(case_id)
        completed = {node.action_id for node in graph.nodes if node.status == "completed"}
        blocked: set[str] = set()
        for edge in graph.edges:
            if edge.relation in {ActionRelation.FOLLOWS, ActionRelation.TRIGGERED_BY} and edge.from_action_id not in completed:
                blocked.add(edge.to_action_id)
        return tuple(node for node in graph.nodes if node.status == "planned" and node.action_id not in blocked)
