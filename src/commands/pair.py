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
    code = context.args[0]
    # Pairing codes are short-lived credentials; remove the submitted message when possible.
    try:
        await message.delete()
    except Exception:
        pass
    try:
        claim = service.claim_telegram(code, telegram_subject=str(user.id))
    except (LookupError, ValueError):
        await message.reply_text("That pairing code is invalid, expired, or already used. Generate a new code in the WebApp.")
        return
    await message.reply_text(
        "Pairing code accepted, but your Telegram account is NOT linked. "
        "Do not assume the accounts are connected. Finish only through an authenticated "
        "Janavani account-linking screen that explicitly reports success; if that screen "
        "is not available in your deployment, request support and generate a new code "
        "when the feature is enabled. Challenge reference: " + claim.pairing_id
    )
