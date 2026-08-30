# JANAVANI — REQUIREMENTS RUNTIME AUDIT

**Date:** 30 August 2026  
**Repository:** `netzen-abm/janavani`  
**Scope:** Root `requirements.txt` versus the canonical runtime direction and currently observable source usage.  
**Decision:** Audit first; do not remove dependencies until runtime ownership and deployment convergence are verified.

## 1. Canonical runtime baseline

The root `Dockerfile` installs `requirements.txt` and starts the API with Uvicorn using the compatibility module `src.web.app:app`. The repository's canonical FastAPI assembly is `src.web.canonical_app:app`. The `Procfile` already targets `src.web.canonical_app:app` directly.

The repository therefore still has deployment ambiguity that must be resolved before dependency deletion is treated as safe.

## 2. Root requirements inventory

| Dependency | Current evidence | Classification | Action now |
|---|---|---|---|
| Flask | Legacy `src/web.py` uses Flask; static runtime audit identifies it as the legacy/simple web path | Legacy runtime dependency | **KEEP temporarily**; remove only after legacy web deployment is retired |
| FastAPI | `src/web/canonical_app.py` imports `FastAPI` and assembles canonical routers | Canonical runtime | **KEEP** |
| uvicorn | Root Dockerfile and Procfile use Uvicorn to start the API | Canonical runtime | **KEEP** |
| python-dotenv | `src/core/config.py` imports `load_dotenv()` | Shared configuration dependency | **KEEP** |
| supabase | `src/storage/supabase.py` imports `create_client`; legacy web path also references Supabase | Existing storage/provider dependency, not yet proven canonical | **KEEP temporarily**; map storage ownership before removal |
| python-telegram-bot | `src/bot_telegram.py` imports Telegram application/handlers | Active channel runtime candidate | **KEEP** |
| requests | `src/adapters/web_client.py` imports and uses `requests.post()` | Existing adapter/runtime dependency | **KEEP** until adapter migration/convergence is complete |
| pandas | `src/services/search_directory.py` and `src/documents/generate_pdf.py` use `pandas.read_csv()` | Existing directory/document runtime dependency | **KEEP for now**; replace only after directory/document migration |
| numpy | No active import was established in the inspected canonical Python runtime; geodesy implementation uses standard-library `math` | Suspected unused root dependency | **DO NOT REMOVE YET**; perform exhaustive import/build/runtime scan first |
| weasyprint | `src/documents/generate_pdf.py` imports `HTML` and calls `write_pdf()` | Existing PDF rendering dependency | **KEEP** while that generator remains in supported runtime |
| reportlab | `src/documents/pdf_generator.py` imports ReportLab and builds PDFs | Existing shared PDF renderer | **KEEP** while this renderer remains supported |
| web3 | Root requirements labels it Future; active production import was not established in the inspected runtime | Future/provider dependency | **Do not remove capability; consider moving to an optional extras/profile later** |
| ipfshttpclient | Root requirements labels it Future; active production import was not established in the inspected runtime | Future/provider dependency | **Do not remove capability; consider moving to an optional extras/profile later** |

## 3. Important architectural distinction

`requirements.txt` is currently mixing three classes:

1. **Canonical runtime dependencies** — required to run the current canonical service.
2. **Legacy/transition dependencies** — required by paths that are being retired or reconciled.
3. **Future capability/provider dependencies** — retained for ecosystem completeness but not required by the current production runtime.

These classes should not be treated identically.

> Optional for the user does not mean removable from the Janavani ecosystem.

For future capabilities such as Web3/IPFS, the preferred cleanup is dependency-profile separation (for example, extras or dedicated provider requirements) rather than deleting the capability from the architecture.

## 4. Known blockers to dependency removal

### Flask

The static runtime map identifies `src/web.py` as a Flask entry point and the current `render.yaml` still starts `python3 src/web.py`. Therefore Flask cannot be safely removed until the deployment target is changed and the legacy path is retired/archived under the repository lifecycle rules.

### Supabase

Supabase is present in the storage layer, but the canonical ownership of citizen/private data is being redesigned around local-first storage. Removing the Python package now could break legacy storage paths or tests. First complete the storage ownership map and runtime verification.

### Pandas

Pandas is still directly used by the office-directory and PDF generation code. Those are candidates for later provider-neutral replacement, but deletion now would be premature.

### NumPy

NumPy is the strongest current candidate for removal from the root runtime requirements because the inspected geodesy implementation uses only Python's `math` module. However, this audit is intentionally not sufficient to delete it: a full repository import/build scan and runtime test must precede removal.

### Web3 / IPFS

These are marked Future in the requirements file. They should not be interpreted as absent from Janavani's ecosystem. If they are not required by the canonical runtime image, they should eventually be isolated into provider-specific optional dependency profiles so the core image remains lean without discarding the capability.

## 5. Recommended dependency convergence

Target structure:

```text
Core runtime
├── FastAPI
├── Uvicorn
├── python-dotenv
└── only dependencies proven by canonical runtime

Channel/provider profiles
├── Telegram
├── Supabase (if retained as a provider)
├── PDF renderers
├── AI providers
├── Web3
└── IPFS
```

The core runtime should contain only dependencies required by the canonical production path. Provider/channel dependencies can remain available through explicit profiles without being mistaken for core requirements.

## 6. Required verification before any deletion

For each candidate dependency:

```text
Static import scan
    ↓
Entry-point scan
    ↓
Test/development usage scan
    ↓
Docker/runtime build
    ↓
Canonical startup
    ↓
Relevant feature test
    ↓
Failure-path test
    ↓
Only then remove
```

No dependency should be removed solely because it is labeled "legacy" or "future".

## 7. Current decision

**No dependency has been removed in this step.**

The audit establishes the evidence needed for a later controlled reduction of `requirements.txt`, with **NumPy as the first candidate for exhaustive verification**, followed by Flask after deployment convergence and any provider-specific packages after profile separation.
