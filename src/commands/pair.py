"""Telegram adapter for the shared Web↔Telegram pairing service."""
from telegram import Update
from telegram.ext import ContextTypes


async def pair(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Claim a Web-issued code in private chat; linking waits for Web confirmation."""
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat
    if message is None or user is None or chat is None:
        return
    if chat.type != "private":
        await message.reply_text("For privacy, identity pairing is available only in a private chat with Janavani.")
        return
    if len(context.args) != 1:
        await message.reply_text("Usage: /pair YOUR_WEB_PAIRING_CODE")
        return
    service = context.application.bot_data.get("identity_pairing_service")
    if service is None:
        await message.reply_text("Identity pairing is not configured. Please use the WebApp without linking Telegram.")
        return
    try:
        claim = service.claim_telegram(context.args[0], telegram_subject=str(user.id))
    except (LookupError, ValueError):
        await message.reply_text("That pairing code is invalid, expired, or already used. Generate a new code in the WebApp.")
        return
    await message.reply_text(
        "Pairing code accepted. Your Telegram account is not linked yet. "
        "Return to the authenticated Janavani WebApp and explicitly confirm the pairing "
        f"before it expires. Challenge: {claim.pairing_id}"
    )
