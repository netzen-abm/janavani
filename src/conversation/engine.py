from conversation.handler import handle_message


async def run_step(update, context):

    """
    Workflow Engine

    Right now it simply delegates
    everything to handler.py.

    Later this engine will decide
    which workflow step to execute.
    """

    await handle_message(update, context)
