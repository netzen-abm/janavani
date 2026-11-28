"""Canonical Telegram command menu for handlers registered on this runtime."""
from telegram import BotCommand


def telegram_bot_commands() -> list[BotCommand]:
    """Expose only commands actually registered by this application composition."""
    return [
        BotCommand("start", "Start Janavani"),
        BotCommand("complaint", "Start a complaint or grievance workflow"),
        BotCommand("search", "Find public-service information"),
        BotCommand("check", "Check a case you own"),
        BotCommand("rate", "Share feedback about the service"),
        BotCommand("ai_draft", "Draft a letter or civic document"),
    ]
