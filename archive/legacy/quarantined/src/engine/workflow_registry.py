"""
Workflow Registry

Registers every supported
citizen workflow.

The engine never knows
what workflows exist.

It asks this registry.
"""

WORKFLOW_REGISTRY = {
    "Complaint": {
        "name": "Complaint",
        "description": "Citizen grievance workflow",
    },

    "RTI": {
        "name": "RTI",
        "description": "Right to Information workflow",
    },
}


def get_workflow(name):
    """
    Return a workflow definition.
    """

    return WORKFLOW_REGISTRY.get(name)


def list_workflows():
    """
    Return every registered workflow.
    """

    return list(WORKFLOW_REGISTRY.values())
