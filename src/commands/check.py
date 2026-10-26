from telegram import Update
from telegram.ext import ContextTypes

from capabilities.civic_case import CivicCaseCapability
from core.civic_case import CivicCase
from src.identity.context import IdentityContext
from src.adapters.telegram.identity import identity_for_telegram_user


def _case_capability(context: ContextTypes.DEFAULT_TYPE) -> CivicCaseCapability:
    capability = context.application.bot_data.get("civic_case_capability")
    if capability is None:
        raise RuntimeError("Telegram civic case capability was not composed")
    return capability


def _telegram_identity(update: Update, context: ContextTypes.DEFAULT_TYPE) -> IdentityContext:
    user_id = getattr(update.effective_user, "id", None)
    if user_id is None:
        raise ValueError("Telegram user identity is required")
    links = context.application.bot_data.get("identity_link_repository")
    if links is None:
        raise RuntimeError("Telegram identity dependencies were not composed")
    return identity_for_telegram_user(user_id, links=links)


def _owned_case(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    capability: CivicCaseCapability,
    case_id: str,
) -> CivicCase | None:
    return capability.get_owned(case_id, identity=_telegram_identity(update, context))


async def _require_private_case_chat(update: Update) -> bool:
    """Prevent Case IDs, statuses and activity from leaking into group chats."""
    message = update.effective_message
    if message is None:
        return False
    chat = update.effective_chat
    if chat is None or chat.type != "private":
        await message.reply_text(
            "For privacy, /cases and /check are available only in a private chat with Janavani."
        )
        return False
    return True


async def cases(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """List recent Cases owned by the current Telegram identity, with metadata only."""
    if not await _require_private_case_chat(update):
        return
    try:
        owned = _case_capability(context).list_owned(
            identity=_telegram_identity(update, context), limit=10
        )
    except Exception:
        await update.message.reply_text("⚠️ Case tracking is temporarily unavailable.")
        return
    if not owned:
        await update.message.reply_text("You have no Cases yet. Use /complaint to start one.")
        return
    rows = [
        f"• {case.case_id} — {case.status} · {case.evidence_count} evidence · "
        f"{case.document_count} documents"
        for case in owned
    ]
    await update.message.reply_text(
        "📄 Your recent Janavani Cases\n\n" + "\n".join(rows)
        + "\n\nUse /check <Case ID> for recent activity."
    )


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the current user's canonical Case status.

    Case reads are routed through the shared CivicCase capability rather than
    accessing the persistence repository directly from the Telegram adapter.
    """
    if not await _require_private_case_chat(update):
        return
    if not context.args:
        await update.message.reply_text(
            "❗ Usage:\n/check <Case ID>\n\nExample:\n/check JNV-1234"
        )
        return

    case_id = context.args[0].strip()
    if not case_id:
        await update.message.reply_text("❗ A Case ID is required.")
        return

    try:
        case = _owned_case(update, context, _case_capability(context), case_id)
    except Exception:
        await update.message.reply_text("⚠️ Case tracking is temporarily unavailable.")
        return

    if case is None:
        await update.message.reply_text(
            "❌ Case not found, or it is not accessible from this Telegram account."
        )
        return

    recent_events = list(case.events)[-3:]
    timeline = "\n".join(
        f"• {event.event_type.value} — {event.occurred_at}"
        for event in recent_events
    ) or "• No lifecycle events recorded"
    await update.message.reply_text(
        (
            "📄 Janavani Case\n\n"
            f"🆔 ID: {case.case_id}\n"
            f"📌 Status: {case.status.value}\n"
            f"📎 Evidence references: {len(case.evidence_refs)}\n"
            f"📄 Document references: {len(case.document_refs)}\n\n"
            "🕒 Recent activity\n"
            f"{timeline}"
        )
    )
