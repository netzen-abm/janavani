from __future__ import annotations

import json
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.error import URLError
from urllib.request import urlopen

ROOT = Path(__file__).parents[1]


def test_web_runtime_survives_independent_telegram_surface_provider_failure() -> None:
    with socket.socket() as listener:
        listener.bind(("127.0.0.1", 0))
        port = listener.getsockname()[1]
    env = {**os.environ, "PYTHONPATH": str(ROOT)}
    web = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "src.web.canonical_app:app",
         "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    endpoint = f"http://127.0.0.1:{port}/liveness"
    try:
        for _ in range(60):
            if web.poll() is not None:
                raise AssertionError("Web runtime exited before becoming healthy")
            try:
                with urlopen(endpoint, timeout=0.5) as response:
                    assert response.status == 200
                    assert json.loads(response.read()) == {"status": "alive"}
                break
            except (OSError, URLError):
                time.sleep(0.25)
        else:
            raise AssertionError("Web runtime did not become healthy")

        failing_surface = """
from src.capabilities.civic_case import CAPABILITY_ID, CivicCaseCreateRequest
from src.core.civic_case import CaseType
from src.identity.context import IdentityContext
from src.identity.principal import IdentityMode, Principal
from src.platform.surface_case_composition import create_surface_case_composition
from src.storage.repositories.case_content import InMemoryCaseContentRepository

class BrokenRepository:
    def save(self, case, *, principal_id=None):
        raise RuntimeError("simulated Telegram provider outage")
    def get(self, case_id, *, principal_id=None):
        raise RuntimeError("simulated Telegram provider outage")

composition = create_surface_case_composition(
    case_repository=BrokenRepository(),
    case_content_repository=InMemoryCaseContentRepository(),
)
identity = IdentityContext(principal=Principal(
    principal_id="citizen:telegram-isolation",
    identity_mode=IdentityMode.AUTHENTICATED,
    capabilities=frozenset({CAPABILITY_ID}),
))
composition.case_capability.create(
    CivicCaseCreateRequest(CaseType.COMPLAINT, "Test", "Failure isolation"),
    identity=identity, source_channel="telegram",
)
"""
        result = subprocess.run(
            [sys.executable, "-c", failing_surface],
            cwd=ROOT, env=env, capture_output=True, text=True, timeout=15,
        )
        assert result.returncode != 0
        assert "simulated Telegram provider outage" in result.stderr

        with urlopen(endpoint, timeout=2) as response:
            assert response.status == 200
            assert json.loads(response.read()) == {"status": "alive"}
    finally:
        web.terminate()
        try:
            web.wait(timeout=5)
        except subprocess.TimeoutExpired:
            web.kill()
            web.wait(timeout=5)
