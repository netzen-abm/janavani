from telegram import Update
from telegram.ext import ContextTypes

from services.rate_office import save_rating


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # ------------------------------------
    # Validate Input
    # ------------------------------------

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

    # ------------------------------------
    # Read Arguments
    # ------------------------------------

    office_id = context.args[0]

    rating = int(context.args[1])

    issue = " ".join(context.args[2:])

    # ------------------------------------
    # Save Rating
    # ------------------------------------

    result = save_rating(
        office_id=office_id,
        rating=rating,
        issue=issue,
    )

    # ------------------------------------
    # Reply
    # ------------------------------------

    await update.message.reply_text(result)
