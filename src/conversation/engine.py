"""
Conversation Engine

The Conversation Engine controls every citizen workflow.

Current Version:
    Router
        ↓
    Engine
        ↓
    Handler

Future Version:
    Router
        ↓
    Engine
        ↓
    Steps
        ↓
    Services
"""

from conversation.handler import handle_message


async def run_step(update, context):
    """
    Main entry point for the Conversation Engine.

    Right now the engine delegates
    to handler.py.

    Later every workflow step
    will execute directly from here.
    """

    await handle_message(update, context)
