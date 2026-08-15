import os
import pytest

def test_development_setup_script_presence_and_execution_permissions():
    """Confirms the high-speed local workspace installation script exists and maintains standard execution rights."""
    target_script_path = "setup_dev.sh"
    
    # Assert path integrity inside master branch architecture definitions
    assert os.path.exists(target_script_path) is True
    
    # Check if the shell orchestrator maintains active operational execution flags
    is_executable = os.access(target_script_path, os.X_OK)
    assert is_executable is True, "The development manager script requires chmod +x privileges to run securely."

def test_global_requirements_file_integrity():
    """Verifies that all sub-module dependencies maps exist across structural folder grids cleanly."""
    assert os.path.exists("src/web_mvp/requirements.txt") is True
    assert os.path.exists("src/web_dioxus/Cargo.toml") is True
