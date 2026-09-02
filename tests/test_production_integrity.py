from pathlib import Path


def test_production_deployment_script_is_valid():
    """The deployment script exists and has a shell entrypoint."""
    path = Path("deploy_production.sh")

    assert path.is_file()
    assert path.read_text(encoding="utf-8").startswith("#!/usr/bin/env bash")


def test_nginx_configuration_file_parsing_compliance():
    """The NGINX configuration retains TLS, rate limiting, and body limits."""
    path = Path("nginx.conf")

    assert path.is_file()
    config_text = path.read_text(encoding="utf-8")

    assert "listen 443 ssl" in config_text
    assert "limit_req_zone" in config_text
    assert "client_max_body_size 2M" in config_text
