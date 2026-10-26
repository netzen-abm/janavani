from __future__ import annotations

import pytest

from src.webapp.runtime_mode import is_production_runtime, runtime_mode


def test_vercel_production_rejects_conflicting_development_override(monkeypatch):
    monkeypatch.setenv("VERCEL_ENV", "production")
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "development")

    with pytest.raises(RuntimeError, match="conflicts with JANAVANI_RUNTIME_MODE"):
        runtime_mode()


def test_vercel_production_without_override_is_production(monkeypatch):
    monkeypatch.setenv("VERCEL_ENV", "production")
    monkeypatch.delenv("JANAVANI_RUNTIME_MODE", raising=False)

    assert runtime_mode() == "production"
    assert is_production_runtime() is True


def test_railway_production_without_override_is_production(monkeypatch):
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.setenv("RAILWAY_ENVIRONMENT_NAME", "production")
    monkeypatch.delenv("JANAVANI_RUNTIME_MODE", raising=False)

    assert runtime_mode() == "production"
    assert is_production_runtime() is True


def test_vercel_preview_defaults_to_test_mode(monkeypatch):
    monkeypatch.setenv("VERCEL_ENV", "preview")
    monkeypatch.delenv("JANAVANI_RUNTIME_MODE", raising=False)

    assert runtime_mode() == "test"
    assert is_production_runtime() is False


def test_explicit_render_or_local_mode_is_respected_outside_vercel_production(monkeypatch):
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "test")

    assert runtime_mode() == "test"
    assert is_production_runtime() is False


def test_unknown_explicit_mode_fails_closed(monkeypatch):
    monkeypatch.delenv("VERCEL_ENV", raising=False)
    monkeypatch.setenv("JANAVANI_RUNTIME_MODE", "prod-ish")

    with pytest.raises(RuntimeError, match="Unsupported JANAVANI_RUNTIME_MODE"):
        runtime_mode()
