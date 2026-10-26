"""Explain Telegram privacy boundaries and bounded encrypted inbox retention."""
from telegram import Update
from telegram.ext import ContextTypes


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Describe Telegram, transient workflow, and encrypted inbox boundaries truthfully."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(
        "Janavani privacy information\n\n"
        "• Telegram receives messages you send to this bot and may retain them under "
        "Telegram's own policies. Janavani cannot erase Telegram's server-side history.\n"
        "• On webhook deployments, the full update payload is encrypted before it is "
        "stored in Janavani's PostgreSQL inbox. The encryption key is configured "
        "separately from the database. Payloads are cleared after successful processing "
        "or terminal dead-lettering and have a maximum 24-hour processing window.\n"
        "• Expiry is enforced by the inbox worker. If the worker is offline at the "
        "deadline, ciphertext can remain in the database until maintenance resumes; "
        "expired payloads are not eligible for processing once the worker resumes.\n"
        "• The bot's guided workflow separately keeps issue text in a process-memory "
        "buffer for up to 15 minutes. This is not a saved Case and is different from "
        "the encrypted webhook retry queue.\n"
        "• If that text expires or the bot process restarts, the unfinished guided workflow "
        "may need to be restarted; Janavani does not recover the expired narrative.\n"
        "• Use /cancel to clear the current in-memory workflow. This does not delete "
        "Telegram messages, a still-retained encrypted inbox payload, downloaded files, "
        "or any separately saved Case.\n"
        "• Share only the minimum necessary information and avoid highly sensitive "
        "details or identity documents unless the workflow clearly requires them.\n"
        "• A pairing code is not a completed account link. Confirm only in an authenticated "
        "Janavani account-linking screen that reports success.\n"
        "• Janavani does not submit a complaint to an authority merely because a draft "
        "was generated. Review and submit it through the stated delivery process."
    )
