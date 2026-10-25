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
        "• The current webhook path processes each parsed Telegram update in request "
        "memory. PostgreSQL stores only the Telegram update ID plus processing/attempt/lease metadata, "
        "not the message body. Failed processing returns a retryable error; durable "
        "business-effect idempotency is still required for commit-before-ack crashes.\n"
        "• A previous webhook implementation persisted full Telegram JSON in a "
        "compatibility queue. If legacy payload-bearing rows remain, the background "
        "worker drains them and clears content on success or terminal dead-lettering. "
        "No independent cleanup job runs while that worker is offline, so legacy rows "
        "may remain until it resumes.\n"
        "• The bot's guided workflow separately keeps issue text in a process-memory "
        "buffer for up to 15 minutes. This is not a saved Case and is separate from the "
        "content-free webhook receipt.\n"
        "• If that text expires or the bot process restarts, the unfinished guided workflow "
        "may need to be restarted; Janavani does not recover the expired narrative. Telegram "
        "may redeliver a webhook update when processing returns a non-2xx result.\n"
        "• Use /cancel to clear the current in-memory workflow. This does not delete "
        "Telegram messages, webhook-inbox records that have not reached a terminal "
        "state, downloaded files, or any separately saved Case.\n"
        "• Until any legacy payload-bearing rows have been verified cleared, share only the minimum "
        "necessary information and avoid highly sensitive details or identity documents.\n"
        "• A pairing code is not a completed account link. Confirm only in an authenticated "
        "Janavani account-linking screen that reports success.\n"
        "• Janavani does not submit a complaint to an authority merely because a draft "
        "was generated. Review and submit it through the stated delivery process."
    )
