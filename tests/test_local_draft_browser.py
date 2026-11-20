"""Real Chromium acceptance for device-local citizen drafts."""
from __future__ import annotations

import json
import socket
import threading
import time
from contextlib import contextmanager
from urllib.parse import parse_qs

import pytest

pytest.importorskip("playwright.sync_api")
from playwright.sync_api import expect, sync_playwright

SCOPE_A = "a" * 64
SCOPE_B = "b" * 64


@contextmanager
def browser_workspace():
    """Run the actual WebApp; mock only authenticated API boundary responses."""
    import uvicorn
    from src.webapp.main import app

    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        port = sock.getsockname()[1]
    server = uvicorn.Server(uvicorn.Config(app, host="127.0.0.1", port=port,
        log_level="critical", access_log=False, lifespan="off"))
    thread = threading.Thread(target=server.run, daemon=True)
    thread.start()
    deadline = time.monotonic() + 15
    while not server.started and time.monotonic() < deadline:
        if not thread.is_alive():
            raise RuntimeError("WebApp test server exited during startup")
        time.sleep(0.1)
    if not server.started:
        server.should_exit = True
        thread.join(timeout=5)
        raise RuntimeError("WebApp test server did not become ready")
    state = {"scope": SCOPE_A, "signed_out": False, "submissions": [], "bodies": []}
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch()
            context = browser.new_context(accept_downloads=True)
            page = context.new_page()
            errors = []
            page.on("dialog", lambda dialog: dialog.accept())
            page.on("pageerror", lambda error: errors.append(str(error)))

            def scope_reply(route):
                if state["signed_out"]:
                    route.fulfill(status=401, content_type="application/json",
                        body='{"error":"Sign-in required"}')
                else:
                    route.fulfill(status=200, content_type="application/json",
                        body=json.dumps({"scope": state["scope"]}))

            def shell_reply(route):
                body = route.request.post_data or ""
                state["bodies"].append(body)
                state["submissions"].append(parse_qs(body, keep_blank_values=True))
                route.fulfill(status=200, content_type="application/json", body=json.dumps({
                    "case_id": "case-browser-accepted", "status": "created",
                    "content_transmitted": False,
                }))

            page.route("**/local-vault/scope", scope_reply)
            page.route("**/submit-issue", shell_reply)
            response = page.goto(f"http://127.0.0.1:{port}/", wait_until="networkidle")
            assert response is not None and response.status == 200
            page.wait_for_function("window.JanavaniLocalVault && document.querySelector('#local-case-draft-form')")
            expect(page.locator("#citizen-input")).to_be_enabled(timeout=10000)
            yield page, state, errors
            context.close()
            browser.close()
    finally:
        server.should_exit = True
        thread.join(timeout=10)


def drafts(page, scope=SCOPE_A):
    return page.evaluate("(scope) => window.JanavaniLocalVault.listDrafts(scope)", scope)


def test_browser_create_reload_open_delete_and_xss_text_handling():
    with browser_workspace() as (page, _state, errors):
        field, status = page.locator("#citizen-input"), page.locator("#local-vault-status")
        first = '<img src=x onerror="window.__draftXssRan = true"> First draft.'
        second = "Second citizen draft survives reload."
        field.fill(first)
        expect(status).to_contain_text("Draft saved", timeout=10000)
        page.locator("#new-local-draft").click()
        expect(status).to_contain_text("New local draft started")
        field.fill(second)
        expect(status).to_contain_text("Draft saved", timeout=10000)
        page.reload(wait_until="networkidle")
        expect(field).to_have_value(second, timeout=10000)
        items = drafts(page)
        assert len(items) == 2
        original = next(item for item in items if item["narrative"] == first)
        assert page.locator("img[onerror]").count() == 0
        assert page.evaluate("window.__draftXssRan === true") is False
        page.locator("#local-draft-list").select_option(original["case_id"])
        page.locator("#open-local-draft").click()
        expect(field).to_have_value(first)
        page.locator("#delete-local-draft").click()
        expect(status).to_contain_text("Selected local draft deleted.")
        assert len(drafts(page)) == 1
        assert errors == []


def test_browser_account_switch_and_logout_fail_closed():
    with browser_workspace() as (page, state, _errors):
        field, status = page.locator("#citizen-input"), page.locator("#local-vault-status")
        field.fill("Private content belonging to account A.")
        expect(status).to_contain_text("Draft saved", timeout=10000)
        state["scope"] = SCOPE_B
        page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
        expect(status).to_contain_text("account changed", timeout=10000)
        expect(field).to_have_value("")
        assert drafts(page, SCOPE_B) == []
        field.fill("Private content belonging to account B.")
        expect(status).to_contain_text("Draft saved", timeout=10000)
        assert len(drafts(page, SCOPE_B)) == 1
        state["scope"] = SCOPE_A
        page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
        expect(status).to_contain_text("account changed", timeout=10000)
        expect(field).to_have_value("Private content belonging to account A.")
        state["signed_out"] = True
        page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
        expect(status).to_contain_text("Sign in again", timeout=10000)
        expect(field).to_be_disabled()
        expect(field).to_have_value("")


def test_browser_import_export_and_metadata_only_case_shell():
    with browser_workspace() as (page, state, _errors):
        field, status = page.locator("#citizen-input"), page.locator("#local-vault-status")
        narrative = "This private citizen narrative remains in browser storage."
        field.fill(narrative)
        expect(status).to_contain_text("Draft saved", timeout=10000)
        with page.expect_download() as event:
            page.locator("#export-local-draft").click()
        path = event.value.path()
        assert path is not None
        with open(path, encoding="utf-8") as handle:
            exported = json.load(handle)
        assert exported["schema"] == "janavani.local-draft.v1"
        assert exported["draft"]["narrative"] == narrative
        assert set(exported["draft"]) == {"case_id", "subject", "narrative"}
        page.locator("#import-local-draft").set_input_files({
            "name": "janavani-draft.json", "mimeType": "application/json",
            "buffer": json.dumps(exported).encode("utf-8"),
        })
        expect(status).to_contain_text("Draft imported into this browser", timeout=10000)
        page.locator("#local-case-draft-form button[type='submit']").click()
        expect(status).to_contain_text("Case case-browser-accepted created", timeout=10000)
        submitted = state["submissions"][0]
        assert set(submitted) == {"case_type", "local_draft_id", "local_vault_scope"}
        assert submitted["case_type"] == ["complaint"]
        assert submitted["local_vault_scope"] == [SCOPE_A]
        assert narrative not in state["bodies"][0]
        linked = next(item for item in drafts(page) if item["server_case_id"] == "case-browser-accepted")
        assert linked["narrative"] == narrative
        page.locator("#clear-local-drafts").click()
        expect(status).to_contain_text("Local drafts for this account were cleared")
        assert drafts(page) == []


def test_browser_storage_quota_and_indexeddb_abort_are_handled():
    with browser_workspace() as (page, _state, errors):
        field, status = page.locator("#citizen-input"), page.locator("#local-vault-status")
        field.fill("Draft saved before storage failure.")
        expect(status).to_contain_text("Draft saved", timeout=10000)
        page.evaluate("""() => {
          window.__originalPut = IDBObjectStore.prototype.put;
          IDBObjectStore.prototype.put = function () {
            throw new DOMException("Simulated quota exhaustion", "QuotaExceededError");
          };
        }""")
        field.fill("This save must fail.")
        expect(status).to_contain_text("Local save failed", timeout=10000)
        page.evaluate("() => { IDBObjectStore.prototype.put = window.__originalPut; }")
        saved = drafts(page)
        assert len(saved) == 1 and saved[0]["narrative"] == "Draft saved before storage failure."
        aborted = page.evaluate("""async (scope) => {
          const original = IDBObjectStore.prototype.put;
          IDBObjectStore.prototype.put = function (...args) {
            const request = original.apply(this, args);
            this.transaction.abort();
            return request;
          };
          try {
            await window.JanavaniLocalVault.saveDraft(scope, {
              case_id: "local-aborted-transaction", subject: "Test", narrative: "Abort this."
            });
            return {ok: true};
          } catch (error) {
            return {ok: false, name: error.name};
          } finally {
            IDBObjectStore.prototype.put = original;
          }
        }""", SCOPE_A)
        assert aborted["ok"] is False and aborted["name"]
        assert not any(x["case_id"] == "local-aborted-transaction" for x in drafts(page))
        assert errors == []
