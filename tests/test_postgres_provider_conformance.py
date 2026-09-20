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
