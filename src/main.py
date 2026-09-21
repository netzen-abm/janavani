"""Janavani application entrypoint compatibility module.

Canonical production Web/API assembly is ``src.web.canonical_app``.
Telegram is an independent surface and has its own explicit runtime entrypoint.
This module is retained only for legacy ``python src/main.py`` invocation and
must not become a second application-composition authority.
"""

from bot_telegram import main as telegram_main


if __name__ == "__main__":
    telegram_main()
