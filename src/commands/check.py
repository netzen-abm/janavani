from telegram import Update
from telegram.ext import ContextTypes

from storage.repositories import CivicCaseRepository


def _case_repository(context: ContextTypes.DEFAULT_TYPE) -> CivicCaseRepository:
    dependencies = context.application.bot_data.get("telegram_generation_dependencies")
    if dependencies is None:
        raise RuntimeError("Telegram case dependencies were not composed")
    return dependencies.case_repository


def _owned_case(update: Update, repository: CivicCaseRepository, case_id: str):
    case = repository.get(case_id)
    if case is None:
        return None

    telegram_user_id = getattr(update.effective_user, "id", None)
    expected_actor = f"telegram:{telegram_user_id}" if telegram_user_id is not None else None
    if expected_actor is None or case.created_by != expected_actor:
        return None
    return case


async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show the current user's canonical Case status.

    This deliberately replaces the legacy JSONL complaint lookup. A Case is
    returned only when its canonical created_by value matches the Telegram
    principal for the current interaction.
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
        case = _owned_case(update, _case_repository(context), case_id)
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
