"""Build-time smoke tests for the exact Vercel WebApp entrypoint."""
from __future__ import annotations

from starlette.testclient import TestClient

from vercel_entrypoint import app


def main() -> None:
    with TestClient(app) as client:
        for path in ("/", "/liveness"):
            response = client.get(path)
            if response.status_code != 200:
                raise RuntimeError(
                    f"WebApp build smoke failed for {path}: HTTP {response.status_code}"
                )
            print(f"WebApp build smoke passed: {path} -> {response.status_code}")

        home = client.get("/")
        if "name=\"narrative\"" not in home.text or "/draft" not in home.text:
            raise RuntimeError("Anonymous incident intake is missing from the homepage")

        narrative = (
            "The streetlights in my lane have not worked for two weeks. "
            "Please repair them and provide copies of the work order and action-taken records."
        )
        preview = client.post("/draft", data={"narrative": narrative, "selection": "auto"})
        if preview.status_code != 200 or "Download PDF" not in preview.text or "RTI" not in preview.text:
            raise RuntimeError("Anonymous complaint/RTI draft smoke test failed")
        if "No account is needed" not in home.text or "does not create a tracked Case" not in preview.text:
            raise RuntimeError("Anonymous workflow privacy/Case-boundary copy is missing")

        download = client.post(
            "/draft/download",
            data={"narrative": narrative, "document_type": "complaint", "document_format": "pdf"},
        )
        if download.status_code != 200 or not download.content.startswith(b"%PDF-"):
            raise RuntimeError("Anonymous PDF download smoke test failed")
        if "no-store" not in download.headers.get("cache-control", ""):
            raise RuntimeError("Anonymous document response must not be cached")
        print("WebApp anonymous intake and transient PDF generation smoke passed")


if __name__ == "__main__":
    main()
