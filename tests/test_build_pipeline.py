import os
import pytest

def test_production_build_script_presence_and_execution_permissions():
    """Confirms the high-speed compilation script exists and maintains standard execution rights."""
    target_script_path = "build_wasm.sh"
    
    # Assert path integrity inside master branch architecture definitions
    assert os.path.exists(target_script_path) is True
    
    # Check if the shell orchestrator maintains active operational execution flags
    is_executable = os.access(target_script_path, os.X_OK)
    assert is_executable is True, "The compilation manager script requires chmod +x privileges to run securely."

def test_dioxus_configuration_parsing_integrity():
    """Checks that the Dioxus settings file is structured correctly and points to the right layout platforms."""
    target_toml_path = "src/web_dioxus/Dioxus.toml"
    assert os.path.exists(target_toml_path) is True
    
    with open(target_toml_path, "r", encoding="utf-8") as f:
        toml_content = f.read()
        
    # Verify the parameters are securely pinned to client browser compilation outputs
    assert 'default_platform = "web"' in toml_content
    assert "[web.assets]" in toml_content
