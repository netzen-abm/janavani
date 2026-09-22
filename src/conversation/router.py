"""Telegram conversation routing adapter.

Routing owns only state-machine dispatch. Classification and civic business
logic belong to canonical capabilities.
"""
from __future__ import annotations

from conversation.engine import run_step


async def route(update, context):
    """Dispatch the Telegram update to the conversation state machine."""
    await run_step(update, context)
