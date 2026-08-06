"""
Base Workflow Step

Every workflow step in Janavani
should inherit from this contract.
"""

from abc import ABC, abstractmethod


class WorkflowStep(ABC):
    """
    Base class for all workflow steps.
    """

    @abstractmethod
    async def execute(self, ctx):
        """
        Execute one workflow step.
        """
        raise NotImplementedError
