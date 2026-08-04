from telegram import Update
from telegram.ext import ContextTypes


async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(
        """
🚧 Complaint PDF generation is temporarily disabled.

The Conversation Engine is currently under development.

This feature will be re-enabled in the next phase.
"""
    )
