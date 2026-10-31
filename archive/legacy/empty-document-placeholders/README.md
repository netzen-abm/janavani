# Archived empty active document placeholders

**Archived on:** 2026-10-28  
**Scope:** four one-newline Python modules previously under `src/documents/`.

| Former active path | Archived path | Original Git blob |
|---|---|---|
| `src/documents/complaint.py` | `archive/legacy/empty-document-placeholders/complaint.py` | `8b137891791fe96927ad78e64b0aad7bded08bdc` |
| `src/documents/grievance.py` | `archive/legacy/empty-document-placeholders/grievance.py` | `8b137891791fe96927ad78e64b0aad7bded08bdc` |
| `src/documents/rti.py` | `archive/legacy/empty-document-placeholders/rti.py` | `8b137891791fe96927ad78e64b0aad7bded08bdc` |
| `src/documents/petition.py` | `archive/legacy/empty-document-placeholders/petition.py` | `8b137891791fe96927ad78e64b0aad7bded08bdc` |

## Evidence and decision

Before retirement, each active file was fetched from the working branch and verified to contain exactly one newline. Each archived counterpart was then fetched again; content and Git blob SHA matched byte-for-byte. The four files shared the same empty blob, so they had no distinct implementation to preserve beyond the exact archived bytes and this audit record.

The active `main` source tree was searched for imports of these module paths. The search found no active imports; the sole broad `src.documents.complaint` hit was inside `docs/archive/legacy/` and referenced a different legacy `complaint_builder` module. The current PR's implementation does not import these placeholders. The canonical document flow now lives in the shared drafting/template capabilities.

They are retired from the active source tree only after archival verification. This action does not remove or rewrite any archived historical material. If future code needs a public compatibility module, it must be introduced deliberately with a documented contract and tests, not by restoring empty placeholders.
