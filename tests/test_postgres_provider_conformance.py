from __future__ import annotations

import re
from pathlib import Path

from src.storage.repositories.provider import SUPPORTED_PROVIDERS


ROOT = Path(__file__).parents[1]


def test_civic_case_durable_provider_set_is_postgres_neutral():
    assert SUPPORTED_PROVIDERS == frozenset({"memory", "postgres"})


def test_active_build_and_runtime_graph_has_no_supabase_import_or_configuration():
    roots = [
        ROOT / "src",
        ROOT / "tests",
        ROOT / ".github",
        ROOT / "scripts",
    ]
    files = [
        path
        for root in roots
        if root.exists()
        for path in root.rglob("*")
        if path.is_file()
        and path != ROOT / "tests/test_postgres_provider_conformance.py"
        and path.suffix in {".py", ".yml", ".yaml", ".toml", ".txt", ".sh", ".json"}
    ]

    forbidden_imports = (
        r"(^|\n)\s*from\s+supabase\s+import\s+",
        r"(^|\n)\s*import\s+supabase(?:\.|\s|$)",
        r"database\.supabase",
        r"supabase_civic_case",
    )
    forbidden_config = (
        r"SUPABASE_URL",
        r"SUPABASE_ANON_KEY",
        r"supabase>=\d",
    )

    for path in files:
        text = path.read_text(encoding="utf-8")
        for pattern in forbidden_imports + forbidden_config:
            assert re.search(pattern, text, flags=re.IGNORECASE) is None, (
                f"active dependency/configuration token {pattern!r} found in {path.relative_to(ROOT)}"
            )


def test_active_deployment_manifests_select_canonical_runtime():
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")
    docker = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    entrypoint = (ROOT / "entrypoint.sh").read_text(encoding="utf-8")

    expected = "src.web.canonical_app:app"
    assert expected in render
    assert expected in docker
    assert expected in entrypoint
    assert "src/web.py" not in render


def test_render_declares_independent_api_webapp_and_telegram_services():
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "name: janavani-web-api" in render
    assert "name: janavani-webapp" in render
    assert "name: janavani-telegram-webhook" in render
    assert render.count("type: web") == 3
    assert "type: worker" not in render
    assert "plan: free" in render
    assert "src.web.canonical_app:app" in render
    assert "src.web.telegram_webhook_app:app" in render

    web_start = "uvicorn src.web.canonical_app:app --host 0.0.0.0 --port $PORT"
    webapp_start = "uvicorn src.webapp.main:app --host 0.0.0.0 --port $PORT"
    telegram_start = "uvicorn src.web.telegram_webhook_app:app --host 0.0.0.0 --port $PORT"
    assert web_start in render
    assert webapp_start in render
    assert telegram_start in render
    assert "subprocess" not in render

def test_telegram_webhook_encrypts_payloads_and_preserves_worker_retries():
    webhook = (ROOT / "src/web/telegram_webhook_app.py").read_text(encoding="utf-8")
    inbox = (ROOT / "src/storage/repositories/postgres_telegram_inbox.py").read_text(
        encoding="utf-8"
    )
    migration = (
        ROOT / "db/migrations/20261025120000_telegram_inbox_encrypted_payloads.sql"
    ).read_text(encoding="utf-8")
    render = (ROOT / "render.yaml").read_text(encoding="utf-8")

    assert "durable_inbox.accept_encrypted" in webhook
    assert "durable_inbox.secure_legacy_payloads" in webhook
    assert "accept_legacy_payload" not in inbox
    assert "MultiFernet" in inbox
    assert "payload IS NOT NULL OR encrypted_payload IS NOT NULL" in inbox
    assert "payload_expires_at" in migration
    assert "JANAVANI_TELEGRAM_INBOX_ENCRYPTION_KEYS" in render

