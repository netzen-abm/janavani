"""Canonical Telegram command catalogue shared by polling and webhook runtimes."""
from telegram import BotCommand


def supported_telegram_commands() -> list[BotCommand]:
    """Return the supported citizen command menu without runtime-specific drift."""
    return [
        BotCommand("start", "Start Janavani"),
        BotCommand("help", "View help and available commands"),
        BotCommand("complaint", "Start a complaint or grievance workflow"),
        BotCommand("search", "Find public-service information"),
        BotCommand("check", "Check a case you own"),
        BotCommand("cases", "List your recent Cases"),
        BotCommand("pair", "Start account pairing; confirmation is required"),
        BotCommand("privacy", "Understand data handling and privacy limits"),
        BotCommand("cancel", "Clear the current in-memory workflow"),
        BotCommand("rate", "Share feedback about the service"),
    ]
