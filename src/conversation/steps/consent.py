from telegram import Update
from telegram.ext import ContextTypes

from conversation.session import get_ephemeral_issue, get_session
from conversation.state import set_state
from conversation.constants import WAITING_FOR_GENERATE
from conversation.steps.generate import TelegramGenerationDependencies, _identity, handle_generate
from src.capabilities.authority import AuthorityCapability
import logging

logger = logging.getLogger(__name__)


async def handle_consent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Collect explicit consent before document generation/submission readiness."""
    user_id = update.effective_user.id
    text = update.message.text.strip().lower()

    if text not in {"yes", "y", "no", "n", "1", "2"}:
        await update.message.reply_text("Please reply YES to continue or NO to cancel.")
        return

    if text in {"no", "n", "2"}:
        await update.message.reply_text("❌ Consent not given. Your case remains unsubmitted.")
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
            "❌ A canonical Case and verified authority are required before consent can be recorded."
        )
        return
    if str(office_id) == "manual":
        await update.message.reply_text(
            "Your Case is saved for tracking, but the manually entered office is not verified. "
            "Use /complaint again and choose a verified authority to generate a document."
        )
        return

    authority_capability: AuthorityCapability | None = (
        context.application.bot_data.get("authority_capability")
    )
    try:
        if authority_capability is None:
            raise LookupError("Authority capability is unavailable")
        authority_capability.require_verified_destination(str(office_id))
        identity = _identity(user_id, links=dependencies.identity_link_repository)
        issue = get_ephemeral_issue(user_id)
        if not issue:
            raise ValueError("Transient issue content expired")
        dependencies.case_capability.hydrate_transient_content(
            case_id,
            identity=identity,
            subject=str(session.get("category") or "Citizen civic issue"),
            narrative=issue,
        )
        dependencies.consent_capability.record_submission_consent(
            case_id,
            scope=f"office:{office_id}",
            identity=identity,
        )
    except (LookupError, PermissionError, ValueError) as exc:
        logger.info(
            "telegram_consent_rejected error_type=%s", type(exc).__name__
        )
        await update.message.reply_text(
            "❌ Consent could not be recorded. Confirm the authority is verified and "
            "your issue has not expired; restart the workflow if needed."
        )
        return
    except Exception as exc:
        logger.warning(
            "telegram_consent_failed error_type=%s", type(exc).__name__
        )
        await update.message.reply_text("❌ Consent service is temporarily unavailable.")
        return

    set_state(user_id, WAITING_FOR_GENERATE)
    await update.message.reply_text(
        "✅ Explicit consent recorded. Preparing a document for your review; nothing will be sent."
    )
    await handle_generate(update, context)
