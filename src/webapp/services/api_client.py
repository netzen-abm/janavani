"""Compatibility import path for the shared canonical Platform API adapter.

Existing WebApp code keeps this module path during convergence. Independently
deployed surfaces should import from src.adapters.janavani_platform_client.
"""
import httpx  # Re-export the same module object for existing adapter tests.
from src.adapters.janavani_platform_client import JanavaniWebAPIClient, client_for_request

__all__ = ["JanavaniWebAPIClient", "client_for_request", "httpx"]
