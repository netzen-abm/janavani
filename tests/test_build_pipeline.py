from pathlib import Path


def test_production_build_script_is_valid():
    """The WASM build script exists and has a shell entrypoint."""
    path = Path("build_wasm.sh")

    assert path.is_file()
    assert path.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")


def test_dioxus_configuration_parsing_integrity():
    """The Dioxus settings target browser compilation."""
    path = Path("src/web_dioxus/Dioxus.toml")

    assert path.is_file()
    content = path.read_text(encoding="utf-8")
    assert 'default_platform = "web"' in content
    assert "[web.assets]" in content
