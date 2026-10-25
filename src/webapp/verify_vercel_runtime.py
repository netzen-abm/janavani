"""Build-time HTTP smoke test for the exact Vercel ASGI entrypoint.

This runs after dependencies are installed and the isolated deployment package
is staged. It deliberately tests only local, non-mutating health routes.
"""
from __future__ import annotations

from starlette.testclient import TestClient
from vercel_entrypoint import app


def main() -> None:
    with TestClient(app) as client:
        for path in ("/", "/liveness"):
            response = client.get(path)
            if response.status_code != 200:
                raise RuntimeError(
                    f"WebApp build smoke failed for {path}: "
                    f"HTTP {response.status_code}"
                )
            print(f"WebApp build smoke passed: {path} -> {response.status_code}")


if __name__ == "__main__":
    main()
