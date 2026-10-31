from telegram import Update
from telegram.ext import ContextTypes

from src.adapters.telegram.identity import identity_for_telegram_user


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Record service feedback through the canonical accountability capability."""
    message = update.effective_message
    if message is None:
        return

    if len(context.args) < 3:
        await message.reply_text(
            "Rate a public service using:\n"
            "/rate <office_id> <1-5> <issue>\n\n"
            "Example: /rate KL-TVM-01 2 Aadhaar update delayed\n\n"
            "1 Very poor · 2 Poor · 3 Average · 4 Good · 5 Excellent"
        )
        return

    office_id = context.args[0]
    try:
        rating = int(context.args[1])
    except ValueError:
        await message.reply_text("Invalid rating. Enter a whole number from 1 to 5.")
        return

    issue = " ".join(context.args[2:])
    try:
        feedback_capability = context.application.bot_data.get("accountability_feedback_capability")
        links = context.application.bot_data.get("identity_link_repository")
        if feedback_capability is None or links is None:
            raise RuntimeError(
                "Canonical Telegram feedback/identity dependencies are not composed"
            )

        actor_ref = None
        if update.effective_user is not None:
            actor_ref = identity_for_telegram_user(
                update.effective_user.id, links=links
            ).principal.principal_id

        feedback = feedback_capability.record(
            office_id=office_id,
            rating=rating,
            issue=issue,
            actor_ref=actor_ref,
            source_channel="telegram",
        )
    except ValueError as exc:
        await message.reply_text(str(exc))
        return

    await message.reply_text(
        f"Saved. Your Feedback ID: {feedback.feedback_id}. Use this to track."
    )
