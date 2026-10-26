"""Managed deployment environments must not fall back to development persistence."""
import pytest

from src.config.runtime import RuntimeConfigurationError, validate_runtime_configuration


def test_vercel_production_cannot_fall_back_to_development_defaults():
    with pytest.raises(RuntimeConfigurationError, match="Production requires durable persistence providers"):
        validate_runtime_configuration(environ={"VERCEL_ENV": "production"})


def test_managed_production_rejects_conflicting_development_mode():
    with pytest.raises(RuntimeConfigurationError, match="conflicts with JANAVANI_RUNTIME_MODE"):
        validate_runtime_configuration(
            environ={"VERCEL_ENV": "production", "JANAVANI_RUNTIME_MODE": "development"}
        )


def test_render_requires_explicit_runtime_mode():
    with pytest.raises(RuntimeConfigurationError, match="Render deployments must set JANAVANI_RUNTIME_MODE"):
        validate_runtime_configuration(environ={"RENDER_SERVICE_ID": "render-service-test"})
