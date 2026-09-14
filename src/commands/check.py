from telegram import Update
from telegram.ext import ContextTypes

from capabilities.civic_case import CivicCaseCapability
from core.civic_case import CivicCase
from identity.context import IdentityContext
from identity.principal import Principal


def _case_capability(context: ContextTypes.DEFAULT_TYPE) -> CivicCaseCapability:
    capability = context.application.bot_data.get("civic_case_capability")
    if capability is None:
        raise RuntimeError("Telegram civic case capability was not composed")
    return capability


def _telegram_identity(update: Update) -> IdentityContext:
    telegram_user_id = getattr(update.effective_user, "id", None)
    if telegram_user_id is None:
        raise ValueError("Telegram user identity is required")
    return IdentityContext(
        principal=Principal(
            principal_id=f"telegram:{telegram_user_id}",
            interface="telegram",
        )
    )


def _owned_case(
    update: Update,
    capability: CivicCaseCapability,
    case_id: str,
) -> CivicCase | None:
    return capability.get_owned(case_id, identity=_telegram_identity(update))


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the current user's canonical Case status.

    Case reads are routed through the shared CivicCase capability rather than
    accessing the persistence repository directly from the Telegram adapter.
    """
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
        case = _owned_case(update, _case_capability(context), case_id)
    except Exception:
        await update.message.reply_text("⚠️ Case tracking is temporarily unavailable.")
        return

    if case is None:
        await update.message.reply_text(
            "❌ Case not found, or it is not accessible from this Telegram account."
        )
        return

    await update.message.reply_text(
        (
            "📄 Janavani Case\n\n"
            f"🆔 ID: {case.case_id}\n"
            f"📌 Status: {case.status.value}\n"
            f"📎 Evidence references: {len(case.evidence_refs)}\n"
            f"📄 Document references: {len(case.document_refs)}"
        )
    )
