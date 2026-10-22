"""One discoverable Telegram command catalogue shared by all runtimes."""
from telegram import BotCommand


def telegram_bot_commands() -> list[BotCommand]:
    """Return the canonical menu for polling and webhook runtimes."""
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
