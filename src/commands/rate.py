from telegram import Update
from telegram.ext import ContextTypes

from services.rate_office import save_rating
from src.authorization.capabilities import PUBLIC_CAPABILITIES
from src.authorization.guards import require_capability
from src.authorization.policy import AuthorizationPolicy
from src.identity.context import anonymous_context


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for anonymous civic office feedback."""
    if len(context.args) < 3:
        await update.message.reply_text(
            """
Usage

/rate office_id rating issue

Example

/rate 3 1 Aadhaar update delayed

Rating

1 = Very Poor

2 = Poor

3 = Average

4 = Good

5 = Excellent
"""
        )
        return

    identity = anonymous_context(
        f"telegram-session:{update.effective_chat.id}",
        interface="telegram",
    )
    require_capability(
        identity,
        "citizen.rating.submit",
        policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
    )

    office_id = context.args[0]
    try:
        rating = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❗ Rating must be a number from 1 to 5.")
        return

    if not 1 <= rating <= 5:
        await update.message.reply_text("❗ Rating must be between 1 and 5.")
        return

    issue = " ".join(context.args[2:])
    result = save_rating(office_id=office_id, rating=rating, issue=issue)
    await update.message.reply_text(result)
