from pathlib import Path


def test_development_setup_script_is_valid():
    """The development setup script exists and has a shell entrypoint."""
    path = Path("setup_dev.sh")

    assert path.is_file()
    assert path.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")


def test_global_requirements_file_integrity():
    """Required active client dependency manifests remain present."""
    assert Path("src/web_mvp/requirements.txt").is_file()
    assert Path("src/web_dioxus/Cargo.toml").is_file()
