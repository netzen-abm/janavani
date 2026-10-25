from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


def test_production_anonymous_drafting_boots_without_optional_oidc():
    env = os.environ.copy()
    env["VERCEL_ENV"] = "production"
    env.pop("JANAVANI_RUNTIME_MODE", None)
    for key in (
        "JANAVANI_OIDC_ISSUER_URL",
        "JANAVANI_OIDC_CLIENT_ID",
        "JANAVANI_OIDC_CLIENT_SECRET",
        "JANAVANI_OIDC_REDIRECT_URI",
        "JANAVANI_WEB_SESSION_SECRET",
        "JANAVANI_IDENTITY_ASSERTION_SECRET",
        "JANAVANI_IDENTITY_ASSERTION_ISSUER",
        "JANAVANI_IDENTITY_ASSERTION_AUDIENCE",
        "JANAVANI_WEB_API_URL",
    ):
        env.pop(key, None)

    smoke = """
from starlette.testclient import TestClient
from src.webapp.main import app

client = TestClient(app)
home = client.get("/")
assert home.status_code == 200
assert "No account is needed" in home.text

narrative = "The streetlight is broken and needs repair."
preview = client.post("/draft", data={"narrative": narrative, "selection": "auto"})
assert preview.status_code == 200
assert "Draft civic complaint" in preview.text

download = client.post(
    "/draft/download",
    data={"narrative": narrative, "document_type": "complaint", "document_format": "pdf"},
)
assert download.status_code == 200
assert download.content.startswith(b"%PDF-")

login = client.get("/auth/login")
assert login.status_code == 503
assert "Sign-in unavailable" in login.text
"""
    completed = subprocess.run(
        [sys.executable, "-c", smoke],
        cwd=REPOSITORY_ROOT,
        env=env,
        capture_output=True,
        text=True,
        timeout=45,
        check=False,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
