"""Telegram authority-search adapter over the shared capability."""
from telegram import Update
from telegram.ext import ContextTypes

from src.capabilities.authority import AuthorityCapability, AuthorityLookupRequest


def _render(results) -> str:
    if not results:
        return "No matching authority was found."
    lines = ["🏛 Authorities"]
    for item in results:
        lines.append(f"• {item.name} — {item.city} — {item.authority_id}")
    return "\n".join(lines)


async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Search public authority metadata without coupling Telegram to storage."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "/search <department> <location>\nExample: /search ration Kochi"
        )
        return
    department = context.args[0]
    city = " ".join(context.args[1:])
    try:
        authority_capability: AuthorityCapability | None = (
            context.application.bot_data.get("authority_capability")
        )
        if authority_capability is None:
            raise RuntimeError("Canonical authority capability was not composed")
        results = authority_capability.search(
            AuthorityLookupRequest(authority_type=department, city=city)
        )
    except ValueError as exc:
        await update.message.reply_text(str(exc))
        return
    except RuntimeError:
        await update.message.reply_text("Authority search is temporarily unavailable.")
        return
    await update.message.reply_text(_render(results))
