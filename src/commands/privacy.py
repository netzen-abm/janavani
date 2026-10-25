"""Explain Telegram privacy boundaries without overstating deletion controls."""
from telegram import Update
from telegram.ext import ContextTypes


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Describe Telegram, transient workflow, and durable inbox boundaries truthfully."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(
        "Janavani privacy information\n\n"
        "• Telegram receives messages you send to this bot and may retain them under "
        "Telegram's own policies. Janavani cannot erase Telegram's server-side history.\n"
        "• On webhook deployments, the full Telegram update payload can be stored in "
        "Janavani's PostgreSQL inbox while work is pending, processing, or retrying. "
        "It is cleared after successful processing or terminal dead-lettering. The "
        "current implementation does not enforce a wall-clock deletion deadline while "
        "the worker is offline; this limitation is under remediation.\n"
        "• The bot's guided workflow separately keeps issue text in a process-memory "
        "buffer for up to 15 minutes. This is not a saved Case, and it does not mean "
        "the original webhook inbox payload is local-only.\n"
        "• If that text expires or the bot process restarts, the unfinished guided workflow "
        "may need to be restarted; Janavani does not recover the expired narrative. A still-pending "
        "webhook update may be replayed from the inbox before it reaches a terminal state.\n"
        "• Use /cancel to clear the current in-memory workflow. This does not delete "
        "Telegram messages, webhook-inbox records that have not reached a terminal "
        "state, downloaded files, or any separately saved Case.\n"
        "• Until the inbox retention deadline is enforced, share only the minimum "
        "necessary information and avoid highly sensitive details or identity documents.\n"
        "• A pairing code is not a completed account link. Confirm only in an authenticated "
        "Janavani account-linking screen that reports success.\n"
        "• Janavani does not submit a complaint to an authority merely because a draft "
        "was generated. Review and submit it through the stated delivery process."
    )
