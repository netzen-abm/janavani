from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_GENERATE
from conversation.steps.generate import TelegramGenerationDependencies


async def handle_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect explicit consent before document generation/submission readiness."""
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if text not in {"yes", "y", "no", "n", "1", "2"}:
        await update.message.reply_text(
            "Please reply YES to continue or NO to cancel."
        )
        return

    if text in {"no", "n", "2"}:
        await update.message.reply_text(
            "❌ Consent not given. Your case remains unsubmitted."
        )
        return

    session = get_session(user_id)
    dependencies = context.application.bot_data.get("telegram_generation_dependencies")
    if not isinstance(dependencies, TelegramGenerationDependencies):
        raise RuntimeError("Telegram generation dependencies were not composed")

    case_id = str(session.get("case_id") or session.get("complaint_id") or "")
    office = session.get("office") or {}
    office_id = office.get("office_id") or office.get("id")
    if not case_id or not office_id:
        await update.message.reply_text(
            "❌ A canonical case and verified office destination are required before consent can be recorded."
        )
        return

    try:
        result = dependencies.consent_capability.record_submission_consent(
            case_id,
            scope=f"office:{office_id}",
            identity=dependencies.identity_factory(user_id),
        )
    except Exception as exc:
        print("ERROR in handle_consent:", exc)
        await update.message.reply_text(
            "❌ Could not record consent. Please try again."
        )
        return

    set_state(user_id, WAITING_FOR_GENERATE)
    await update.message.reply_text(
        "✅ Consent recorded. Generating your document for review/printing."
    )
