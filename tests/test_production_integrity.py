import os
import pytest

def test_production_deployment_orchestration_file_permissions():
    """Guarantees the global release script maintains appropriate execution properties."""
    target_path = "deploy_production.sh"
    
    # Check that deployment files are present across active project paths
    assert os.path.exists(target_path) is True
    
    # Check for execution permissions
    is_executable = os.access(target_path, os.X_OK)
    assert is_executable is True, "The production deployment runner requires execute permissions to run cleanly."

def test_nginx_configuration_file_parsing_compliance():
    """Confirms that the public NGINX routing script exists and enforces TLS protocols."""
    proxy_config_path = "nginx.conf"
    assert os.path.exists(proxy_config_path) is True
    
    with open(proxy_config_path, "r", encoding="utf-8") as f:
        config_text = f.read()
        
    # Ensure security filters and proxy parameters are declared correctly
    assert "listen 443 ssl" in config_text
    assert "limit_req_zone" in config_text
    assert "client_max_body_size 1M" in config_text
