import os


def test_production_deployment_orchestration_file_permissions():
    """Guarantees the global release script maintains executable permissions."""
    target_path = "deploy_production.sh"
    assert os.path.exists(target_path) is True
    assert os.access(target_path, os.X_OK) is True


def test_nginx_configuration_file_parsing_compliance():
    """Confirms the public NGINX routing configuration enforces core limits."""
    proxy_config_path = "nginx.conf"
    assert os.path.exists(proxy_config_path) is True

    with open(proxy_config_path, "r", encoding="utf-8") as f:
        config_text = f.read()

    assert "listen 443 ssl" in config_text
    assert "limit_req_zone" in config_text
    assert "client_max_body_size 2M" in config_text
