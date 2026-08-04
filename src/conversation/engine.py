from conversation.workflow import WORKFLOWS
from conversation.handler import handle_message


async def run_step(update, context):

    """
    Workflow Engine

    Version 2

    For now,
    conversation logic still lives in handler.py.

    Soon,
    this engine will execute workflow steps directly.
    """

    await handle_message(update, context)
