"""Legacy compatibility entrypoint.

Canonical Web/API runtime: src.web.canonical_app:app.
Canonical Telegram runtime: src.bot_telegram:main.

This module intentionally does not compose either surface and is retained
only for legacy invocation compatibility.
"""

from __future__ import annotations


def main() -> None:
    raise SystemExit(
        "Use 'uvicorn src.web.canonical_app:app' for the Web/API surface "
        "or 'python -m src.bot_telegram' for the Telegram surface."
    )


if __name__ == "__main__":
    main()
