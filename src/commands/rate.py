from telegram import Update
from telegram.ext import ContextTypes

from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
from src.storage.repositories.accountability_feedback_jsonl import JsonlAccountabilityFeedbackRepository


feedback_capability = AccountabilityFeedbackCapability(JsonlAccountabilityFeedbackRepository())


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

5 = Excellent
"""
        )
        return

    office_id = context.args[0]
    try:
        rating = int(context.args[1])
    except ValueError:
        await update.message.reply_text("Invalid rating: must be an integer between 1 and 5.")
        return

    issue = " ".join(context.args[2:])
    actor_ref = None
    if update.effective_user is not None:
        actor_ref = f"telegram:{update.effective_user.id}"

    try:
        feedback = feedback_capability.record(
            office_id=office_id,
            rating=rating,
            issue=issue,
            actor_ref=actor_ref,
            source_channel="telegram",
        )
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return

    await update.message.reply_text(
        f"Saved. Your Feedback ID: {feedback.feedback_id}. Use this to track."
    )
