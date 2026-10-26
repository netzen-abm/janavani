"""Legacy compatibility entrypoint.

Canonical Web/API runtime: src.web.canonical_app:app.
Canonical Telegram runtime: src.web.telegram_webhook_app:app (HTTPS webhook; polling is retired).

This module intentionally does not compose either surface and is retained
only for legacy invocation compatibility.
"""

from __future__ import annotations


def main() -> None:
    raise SystemExit(
        "Use 'uvicorn src.web.canonical_app:app' for the Web/API surface "
        "or 'uvicorn src.web.telegram_webhook_app:app' for the Telegram webhook surface."
    )


if __name__ == "__main__":
    main()
