from telegram import Update
from telegram.ext import ContextTypes

from capabilities.feedback_file import JsonlFeedbackCapability


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for the shared Feedback capability."""
    if len(context.args) < 3:
        await update.message.reply_text(
            """Usage

/rate office_id rating issue

Example

/rate 3 1 Aadhaar update delayed

Rating

1 = Very Poor
2 = Poor
3 = Average
4 = Good
5 = Excellent"""
        )
        return

    authority_id = context.args[0]
    try:
        rating = int(context.args[1])
    except ValueError:
        await update.message.reply_text("❌ Rating must be a number from 1 to 5.")
        return

    comment = " ".join(context.args[2:])
    result = JsonlFeedbackCapability().submit_rating(
        authority_id=authority_id,
        rating=rating,
        comment=comment,
    )

    await update.message.reply_text(
        result.message or "Feedback could not be recorded."
    )
