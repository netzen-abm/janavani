from telegram import Update
from telegram.ext import ContextTypes

from src.authorization.capabilities import PUBLIC_CAPABILITIES
from src.authorization.guards import require_capability
from src.authorization.policy import AuthorizationPolicy
from src.identity.context import anonymous_context
from services.search_directory import search_office


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telegram adapter for the public office-search capability."""
    if len(context.args) < 2:
        await update.message.reply_text(
            """
Usage

/search department location

Example

/search ration Kochi

/search village Kannur

/search police Kozhikode
"""
        )
        return

    identity = anonymous_context(
        f"telegram-session:{update.effective_chat.id}",
        interface="telegram",
    )
    require_capability(
        identity,
        "public.search_office",
        policy=AuthorizationPolicy(anonymous_capabilities=PUBLIC_CAPABILITIES),
    )

    department = context.args[0]
    location = " ".join(context.args[1:])
    result = search_office(department, location)
    await update.message.reply_text(result)
