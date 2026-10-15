"""Explain Telegram privacy boundaries without overstating deletion controls."""
from telegram import Update
from telegram.ext import ContextTypes


async def privacy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Describe what Janavani controls and what remains under Telegram's control."""
    message = update.effective_message
    if message is None:
        return
    await message.reply_text(
        "Janavani privacy information\n\n"
        "• Telegram receives messages you send to this bot and may retain them under "
        "Telegram's own policies. Janavani cannot erase Telegram's server-side history.\n"
        "• Janavani keeps the current Telegram workflow in process memory. Issue text "
        "used by the guided workflow is short-lived; it is not the same as a saved case.\n"
        "• Use /cancel to clear the current in-memory workflow. This does not delete "
        "Telegram messages, downloaded files, or any separately saved case.\n"
        "• Do not send identity documents or sensitive details unless they are necessary.\n"
        "• A pairing code is not a completed account link. Confirm only in an authenticated "
        "Janavani account-linking screen that reports success.\n"
        "• Janavani does not submit a complaint to an authority merely because a draft "
        "was generated. Review and submit it through the stated delivery process."
    )
