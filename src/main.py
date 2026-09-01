"""Canonical application entrypoint.

Telegram is currently the active transport adapter.  Other ecosystem surfaces
must remain independently deployable and should not be coupled to this module.
"""

from bot_telegram import main as telegram_main


if __name__ == "__main__":
    telegram_main()
