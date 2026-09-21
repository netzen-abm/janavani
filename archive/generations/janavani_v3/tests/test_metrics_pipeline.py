import pytest
import fakeredis
from fastapi.testclient import TestClient
from src.web.app import app

def test_telemetry_endpoint_security_rejection_mechanics():
    """Confirms that the metrics endpoint rejects requests lacking valid interface tokens."""
    client = TestClient(app)
    
    # Assert that requests missing authentication headers are blocked with a 403 status code
    response = client.get("/api/v3/core/metrics")
    assert response.status_code == 403

def test_prometheus_response_formatting_compliance():
    """Verifies that the metrics route outputs compliant plain-text OpenMetrics rows."""
    client = TestClient(app)
    headers = {"X-Janavani-Interface-Token": "prometheus-scraper-token"}
    
    response = client.get("/api/v3/core/metrics", headers=headers)
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/plain")
    
    metrics_output = response.text
    # Confirm standard Prometheus help and counter formatting strings are intact
    assert "# HELP janavani_host_cpu_utilization_percent" in metrics_output
    assert "janavani_host_memory_usage_bytes" in metrics_output
