from telegram import Update
from telegram.ext import ContextTypes

from conversation.state import set_state
from conversation.constants import WAITING_FOR_ISSUE
from src.authorization.capabilities import PUBLIC_CAPABILITIES
from src.authorization.guards import require_capability
from src.authorization.policy import AuthorizationPolicy
from src.identity.context import anonymous_context


async def complaint(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for starting the public complaint workflow."""
    identity = anonymous_context(
        f"telegram-session:{update.effective_chat.id}",
        interface="telegram",
    )
    require_capability(
        identity,
        "citizen.complaint.start",
        policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
    )

    set_state(update.effective_user.id, WAITING_FOR_ISSUE)
    await update.message.reply_text(
        """📝 Please describe your issue.

Example:
My road has been broken for 3 months
"""
    )
