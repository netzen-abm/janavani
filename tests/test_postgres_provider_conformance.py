from pathlib import Path

import pytest

from src.storage.repositories.provider import SUPPORTED_PROVIDERS


ROOT = Path(__file__).parents[1]


def test_civic_case_durable_provider_set_is_postgres_neutral():
    assert SUPPORTED_PROVIDERS == frozenset({"memory", "postgres"})


@pytest.mark.parametrize(
    "relative_path",
    [
        "requirements.txt",
        "pyproject.toml",
        ".env.example",
        ".github/workflows/ci.yml",
        "src/storage/repositories/provider.py",
        "src/storage/repositories/__init__.py",
        "src/core/config.py",
    ],
)
def test_active_runtime_build_surface_has_no_supabase_dependency(relative_path):
    path = ROOT / relative_path
    text = path.read_text(encoding="utf-8").lower()
    forbidden = (
        "from supabase import",
        "import supabase",
        "supabase>=2.",
        "supabase_civic_case",
        "supabase_url",
        "supabase_anon_key",
    )
    assert not any(token in text for token in forbidden), relative_path
