"""WebApp landing and case-creation entry routes.

Keep page entry and the create-case consent boundary together; lifecycle,
review, explicit submission consent and artifact routes remain in
src.webapp.case_workspace. The canonical API remains authoritative for records.
"""
from __future__ import annotations

from collections.abc import Callable
from typing import Any

from fasthtml.common import (
    A, Button, Div, Form, H1, H2, H3, Img, Input, Label, P, Script, Textarea, Title,
)
from starlette.requests import Request


def register_webapp_entry_routes(
    rt, *, client_factory: Callable[[Request], Any]
) -> None:
    """Register the WebApp home page and explicitly consented case creation."""

    @rt("/local-vault/scope")
    def get_local_vault_scope(request: Request):
        """Proxy the authenticated account namespace without exposing identity data."""
        try:
            return client_factory(request).get_local_vault_scope()
        except (RuntimeError, ValueError):
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Sign-in required"}, status_code=401)
        except Exception:
            from starlette.responses import JSONResponse
            return JSONResponse({"error": "Local vault scope unavailable"}, status_code=503)

    @rt("/")
    def get_home():
        """Render the case-workspace entry point."""
        return (
            Title("🇮🇳 Janavani — Citizen Action Hub"),
            Div(
                Div(
                    Div(
                        Img(
                            src="/brand-assets/brand/janavani-mark",
                            alt="",
                            width="64",
                            height="64",
                        ),
                        H1("JANAVANI"),
                        cls="brand-lockup",
                    ),
                    P(
                        "Create and review a civic case through the shared "
                        "JanaVani platform."
                    ),
                    A(
                        "Start a letter, complaint or RTI draft",
                        href="/ai-drafting",
                        style="display: inline-block; margin-top: 1rem;",
                    ),
                    style="text-align: center; margin-bottom: 3rem;",
                ),
                Div(
                    H3("📝 Create a Civic Case"),
                    P(
                        "Your narrative is saved in this browser first. Creating a Case sends "
                        "only minimal lifecycle metadata to the canonical API."
                    ),
                    Form(id="local-case-draft-form", action="/submit-issue", method="post")(
                        Input(type="hidden", name="case_type", value="complaint"),
                        Textarea(
                            name="citizen_input",
                            id="citizen-input",
                            placeholder="Describe the civic issue...",
                            rows=6,
                            required=True,
                            maxlength=20000,
                        ),
                        P(id="local-vault-status", role="status"),
                        Button("Create Case", type="submit", cls="button-primary"),
                    ),
                    Script("""
                    (() => {
                      const form = document.getElementById("local-case-draft-form");
                      const field = document.getElementById("citizen-input");
                      const status = document.getElementById("local-vault-status");
                      if (!form || !field || !window.JanavaniLocalVault) return;
                      let scope = null;
                      let caseId = null;
                      const setStatus = (message) => { status.textContent = message; };
                      const save = async () => {
                        if (!scope || !caseId) return;
                        await window.JanavaniLocalVault.saveDraft(scope, {
                          case_id: caseId, subject: "Civic complaint", narrative: field.value
                        });
                        setStatus("Draft saved in this browser. It is not a server backup.");
                      };
                      (async () => {
                        try {
                          scope = await window.JanavaniLocalVault.resolveScope();
                          caseId = "local-" + (window.crypto && crypto.randomUUID
                            ? crypto.randomUUID() : Date.now().toString(36) + Math.random().toString(36).slice(2));
                          const drafts = await window.JanavaniLocalVault.listDrafts(scope);
                          const latest = drafts.sort((a, b) => b.updated_at.localeCompare(a.updated_at))[0];
                          if (latest) {
                            caseId = latest.case_id;
                            field.value = latest.narrative || "";
                            setStatus("Your latest local draft was restored in this browser.");
                          } else {
                            setStatus("Drafts stay in this browser until you choose to create a Case.");
                          }
                        } catch (error) {
                          field.disabled = true;
                          setStatus("Local draft storage is unavailable. No content will be sent. " + error.message);
                        }
                      })();
                      field.addEventListener("input", () => {
                        save().catch(error => setStatus("Local save failed. Do not navigate away. " + error.message));
                      });
                      form.addEventListener("submit", async (event) => {
                        event.preventDefault();
                        try {
                          if (!scope) throw new Error("Sign in and verify local storage before continuing.");
                          await save();
                          const response = await fetch("/submit-issue", {
                            method: "POST",
                            credentials: "same-origin",
                            headers: {"Content-Type": "application/x-www-form-urlencoded"},
                            body: new URLSearchParams({
                              case_type: "complaint",
                              local_draft_id: caseId
                            })
                          });
                          if (!response.ok) throw new Error("Could not create the Case shell.");
                          document.open();
                          document.write(await response.text());
                          document.close();
                        } catch (error) {
                          setStatus("Case not created. Your local draft remains in this browser. " + error.message);
                        }
                      });
                    })();
                    """),
                    cls="card",
                ),
                cls="container",
            ),
        )

    @rt("/submit-issue")
    def post(
        request: Request,
        local_draft_id: str = "",
        case_type: str = "complaint",
    ):
        """Create only a metadata shell; citizen narrative stays in browser storage."""
        import re
        if not re.fullmatch(r"local-[a-zA-Z0-9-]{8,80}", local_draft_id):
            return Div(
                Div(H3("Local draft required"), P("No Case was created. Save a draft in your browser first."), A("Return", href="/"), cls="card")
            )
        try:
            result = client_factory(request).create_case_shell(case_type=case_type)
        except (RuntimeError, ValueError):
            return Div(Div(H3("Sign-in required"), P("Authenticate before creating a Case shell. Your draft remains in this browser."), A("Return", href="/"), cls="card"))
        except Exception:
            return Div(Div(H3("Case creation unavailable"), P("No Case was created. Your local draft remains in this browser."), A("Return", href="/"), cls="card"))
        if "error" in result:
            return Div(Div(H3("Case creation failed"), P(result["error"]), A("Return", href="/"), cls="card"))
        return Div(
            Div(
                H2("Civic Case shell created"),
                P(f"Case ID: {result.get('case_id')}"),
                P(f"Status: {result.get('status')}"),
                P("Your narrative remains in this browser. The server received Case metadata only. This Case shell does not contain your complaint text."),
                P("Do not clear this browser's site data if you need the local draft. Cross-device recovery is not available in device-first mode."),
                A("Return to dashboard", href="/"),
                cls="card",
            )
        )
