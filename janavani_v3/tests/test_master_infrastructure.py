import os
import pytest

def test_production_deployment_scripts_permissions():
    """Guarantees that all required deployment and automation shell scripts maintain appropriate execution flags."""
    required_scripts = [
        "deploy_production.sh",
        "run_all_tests.sh",
        "build_wasm.sh",
        "setup_dev.sh"
    ]
    
    for script in required_scripts:
        # Check path presence across workspace directories
        assert os.path.exists(script) is True, f"Required automation file '{script}' is missing from the repository."
        
        # Verify active executable status flags are set
        is_executable = os.access(script, os.X_OK)
        assert is_executable is True, f"The script file '{script}' requires execute privileges (chmod +x) to run cleanly."

def test_documentation_files_presence():
    """Confirms that the necessary onboarding manuals and development handbooks are present in the workspace root."""
    required_docs = [
        "DEVELOPER_GUIDE.md",
        "CONTRIBUTING.md"
    ]
    
    for doc in required_docs:
        assert os.path.exists(doc) is True, f"Mandatory system documentation handbook '{doc}' is missing."
