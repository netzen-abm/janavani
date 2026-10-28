from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from core.config import Config
from commands.check import check
from commands.start import start
from commands.search import search
from commands.rate import rate
from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
from src.platform.composition import create_accountability_feedback_repository
from commands.complaint import complaint
from src.commands.ai_draft import ai_draft_command, handle_civic_draft_callback
from conversation.router import route
from conversation.steps.format import handle_format
from conversation.steps.generate import create_telegram_generation_dependencies
from src.platform.surface_case_composition import create_surface_case_composition


def build_application(*, token: str | None = None) -> Application:
    """Compose a testable Telegram runtime without starting network polling."""
    bot_token = token or Config.TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

    application = Application.builder().token(bot_token).build()

    # Compose the shared ecosystem graph once at the bot application boundary.
    composition = create_surface_case_composition()
    case_repository = composition.case_repository
    case_capability = composition.case_capability
    application.bot_data["surface_case_composition"] = composition
    application.bot_data["case_repository"] = case_repository
    application.bot_data["civic_case_capability"] = case_capability
    application.bot_data["civic_action_capability"] = composition.civic_action_capability
    application.bot_data["consent_repository"] = composition.consent_repository
    application.bot_data["evidence_capability"] = composition.evidence_capability
    application.bot_data["authority_capability"] = composition.authority_capability
    application.bot_data["identity_link_repository"] = composition.identity_link_repository
    application.bot_data["accountability_feedback_capability"] = AccountabilityFeedbackCapability(
        create_accountability_feedback_repository(
            provider_composition=composition.provider_composition
        )
    )
    application.bot_data["civic_action_vertical_slice"] = composition.civic_action_vertical_slice
    application.bot_data["telegram_generation_dependencies"] = (
        create_telegram_generation_dependencies(
            case_repository=case_repository,
            case_capability=case_capability,
            civic_action_capability=composition.civic_action_capability,
            consent_capability=composition.consent_capability,
            identity_link_repository=composition.identity_link_repository,
        )
    )

    # Specific feature callbacks must precede the general format callback.
    application.add_handler(CallbackQueryHandler(handle_civic_draft_callback, pattern=r"^civicdraft:"))
    application.add_handler(CallbackQueryHandler(handle_format))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("complaint", complaint))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("ai_draft", ai_draft_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route))
    return application


def main() -> None:
    """Fail closed: the standalone polling entry point is retired."""
    raise RuntimeError(
        "Telegram polling is disabled. Start the HTTPS webhook service at "
        "src.web.telegram_webhook_app:app instead."
    )


if __name__ == "__main__":
    main()
