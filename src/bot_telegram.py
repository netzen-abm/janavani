import asyncio

from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)

from core.config import Config
from src.config.runtime import validate_runtime_configuration
from conversation.session import purge_expired_ephemeral_issues
from src.commands.catalogue import telegram_bot_commands
from src.commands.account import account
from src.commands.ai_draft import ai_draft_command, handle_civic_draft_callback
from commands.check import cases, check
from commands.cancel import cancel
from commands.pair import pair
from commands.privacy import privacy
from commands.start import help_command, start
from commands.search import search
from commands.rate import rate
from src.capabilities.accountability_feedback import AccountabilityFeedbackCapability
from src.platform.composition import create_accountability_feedback_repository
from commands.complaint import complaint
from conversation.router import route
from conversation.steps.generate import create_telegram_generation_dependencies
from conversation.steps.format import handle_format
from src.platform.surface_case_composition import create_surface_case_composition
from src.identity.pairing import IdentityPairingService
from src.platform.composition import create_identity_pairing_repository


async def _set_bot_commands(application: Application) -> None:
    """Publish the canonical bot command catalogue."""
    await application.bot.set_my_commands(telegram_bot_commands())


async def _post_init(application: Application) -> None:
    """Initialize shared commands and start privacy cleanup for transient text."""
    await _set_bot_commands(application)
    _start_ephemeral_issue_cleanup(application)


async def _cleanup_expired_issue_text() -> None:
    while True:
        await asyncio.sleep(30)
        purge_expired_ephemeral_issues()


def _start_ephemeral_issue_cleanup(application: Application) -> None:
    task = application.bot_data.get("janavani_ephemeral_issue_cleanup")
    if task is None or task.done():
        application.bot_data["janavani_ephemeral_issue_cleanup"] = asyncio.create_task(
            _cleanup_expired_issue_text()
        )


async def _stop_ephemeral_issue_cleanup(application: Application) -> None:
    task = application.bot_data.pop("janavani_ephemeral_issue_cleanup", None)
    if task is None:
        return
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass


def build_application(*, token: str | None = None) -> Application:
    """Compose a testable Telegram runtime without starting network polling."""
    bot_token = token or Config.TELEGRAM_BOT_TOKEN
    if not bot_token:
        raise ValueError("TELEGRAM_BOT_TOKEN is not configured.")

    # Do not let a production Telegram process silently compose memory-backed domains.
    validate_runtime_configuration()

    application = (
        Application.builder()
        .token(bot_token)
        .post_init(_post_init)
        .post_stop(_stop_ephemeral_issue_cleanup)
        .build()
    )

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
    # Pairing across independently deployed processes requires shared PostgreSQL.
    pairing_service = None
    if composition.provider_composition.provider_for("external_identity_links") == "postgres":
        pairing_repository = create_identity_pairing_repository(
            provider_composition=composition.provider_composition,
            identity_link_repository=composition.identity_link_repository,
        )
        pairing_service = IdentityPairingService(pairing_repository)
    application.bot_data["identity_pairing_service"] = pairing_service
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

    # Keep feature-specific callbacks ahead of broad handlers to prevent shadowing.
    application.add_handler(CallbackQueryHandler(handle_civic_draft_callback, pattern=r"^civicdraft:"))
    application.add_handler(CallbackQueryHandler(handle_format, pattern=r"^(pdf|docx)$"))
    application.add_handler(CallbackQueryHandler(route))
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("account", account))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("cancel", cancel))
    application.add_handler(CommandHandler("ai_draft", ai_draft_command))
    application.add_handler(CommandHandler("privacy", privacy))
    application.add_handler(CommandHandler("search", search))
    application.add_handler(CommandHandler("rate", rate))
    application.add_handler(CommandHandler("complaint", complaint))
    application.add_handler(CommandHandler("check", check))
    application.add_handler(CommandHandler("cases", cases))
    application.add_handler(CommandHandler("pair", pair))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, route))
    return application


def main() -> None:
    """Fail closed so the retired polling runtime cannot start accidentally."""
    raise RuntimeError(
        "Telegram polling is disabled. Use the HTTPS webhook service configured for "
        "src.web.telegram_webhook_app:app; do not call run_polling()."
    )


if __name__ == "__main__":
    main()
