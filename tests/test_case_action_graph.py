from src.core.capabilities.case_action_graph import SharedCaseActionGraph
from src.core.contracts.case_action_graph import ActionRelation, CivicAction


def test_parallel_actions_are_available_together():
    graph = SharedCaseActionGraph()
    complaint = graph.add_action("case-1", CivicAction.COMPLAINT)
    rti = graph.add_action("case-1", CivicAction.RTI)
    graph.connect(complaint, rti, ActionRelation.PARALLEL)
    assert {x.action for x in graph.next_actions("case-1")} == {CivicAction.COMPLAINT, CivicAction.RTI}


def test_followup_is_blocked_until_parent_completes():
    graph = SharedCaseActionGraph()
    complaint = graph.add_action("case-2", CivicAction.COMPLAINT)
    followup = graph.add_action("case-2", CivicAction.FOLLOW_UP)
    graph.connect(complaint, followup, ActionRelation.FOLLOWS, trigger="verified procedural trigger")
    assert [x.action for x in graph.next_actions("case-2")] == [CivicAction.COMPLAINT]
    graph.transition(complaint.action_id, "completed")
    assert [x.action for x in graph.next_actions("case-2")] == [CivicAction.FOLLOW_UP]


def test_actions_cannot_cross_case_boundaries():
    graph = SharedCaseActionGraph()
    left = graph.add_action("case-a", CivicAction.COMPLAINT)
    right = graph.add_action("case-b", CivicAction.RTI)
    try:
        graph.connect(left, right, ActionRelation.PARALLEL)
    except ValueError:
        pass
    else:
        raise AssertionError("cross-case action connection should fail")
