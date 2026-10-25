# Archived WebApp Constitutional Bill-Review Route

**Archived:** 25 October 2026  
**Status:** Historical workflow preserved; do not treat as a supported production journey.

## Previous user-facing intent

The legacy route `/bill-review/{bill_code}` displayed a constitutional audit report, accepted optional citizen observations, and offered PDF/DOCX download controls for an objection document. The old page described assessments around Articles 14, 19 and 21 of the Constitution and suggested that the citizen could print and send the document.

The corresponding `/dispatch-objection` handler called `JanavaniWebAPIClient.download_constitutional_objection`, which intentionally returns `None` to avoid reviving retired dispatch behavior. Therefore the page could not complete its advertised workflow.

## Why the live route now fails closed

The canonical API does contain a `ConstitutionalObjectionCapability` and a `/api/v1/constitutional/generate-objection` endpoint. However, the endpoint requires an authenticated, owner-scoped Case of type `objection`, citizen reasoning, and a verified authority destination. The old WebApp form bypassed those prerequisites.

The currently inspected `src/core/legislative_monitor.py` uses a hard-coded bill registry, and those profile entries do not provide source references/provenance fields. A working download button must not turn an unverified profile into apparently authoritative constitutional analysis.

The live routes were therefore changed to:
- `GET /bill-review/{bill_code}`: return an explicit unavailable response explaining the missing source-provenance gate, with no assessment or document generated.
- `POST /dispatch-objection`: return HTTP 410 (Gone), stating that no file was generated and nothing was transmitted.

This is a fail-closed interim state, not a claim that the full constitutional workflow is complete.

## Reactivation acceptance requirements

Do not re-enable this journey until all of the following are verified:

1. Bill profiles have authoritative source references, source dates/version, and documented provenance. The UI clearly distinguishes official text from analysis and citizen commentary.
2. The citizen is authenticated and creates or selects an owned canonical `objection` Case.
3. A verified authority destination is selected from the canonical Authority capability and revalidated at confirmation time.
4. Document generation calls the canonical Constitutional Objection capability; no parallel generation logic is added to the WebApp.
5. Bill codes and filename/header values are validated/sanitized; the download response uses no-store and appropriate content/security headers.
6. The citizen reviews the generated document and explicitly downloads it. Janavani does not email, transmit or submit it.
7. Tests cover missing/unverified profiles, missing authority, wrong Case type/owner, unsupported format, empty artifact, header injection, upstream failures and the successful end-to-end path.
8. Runtime acceptance confirms that the WebApp and API use the trusted identity/session path and do not persist raw citizen content outside the approved retention policy.

## Canonical references

- `src/webapp/main.py` — live fail-closed routes.
- `src/webapp/services/api_client.py` — provider-neutral WebApp HTTP adapter.
- `src/web/constitutional_router.py` — canonical API endpoint.
- `src/capabilities/constitutional_objection.py` — canonical capability.
- [Issue #220](https://github.com/netzen-abm/janavani/issues/220) — reactivation/retirement acceptance tracking.
