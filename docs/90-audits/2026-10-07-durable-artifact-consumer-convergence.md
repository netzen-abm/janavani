# Durable Artifact Consumer Convergence Audit — 2026-10-07

## Decision

The durable artifact stack is retained as an **independent persistence boundary**, but it is not the default orchestration path for every document-generation use case.

### Consumer classification

| Consumer | Current behavior | Boundary | Decision |
| --- | --- | --- | --- |
| `src/documents/artifact_service.py` | Renders and can persist through blob store | persistence/provider | **KEEP** |
| `src/capabilities/civic_action_capability.py` | `generate_reviewable_artifact()` persists artifact metadata + bytes | durable artifact capability | **KEEP as explicit durable API**; do not use as the ephemeral WebApp default |
| `src/capabilities/civic_action_vertical_slice_document.py` | Generates durable packages and resolves approved stored artifacts | persistence + delivery | **KEEP** for explicit durable/download package workflow |
| `src/capabilities/constitutional_objection.py` | Generates durable reviewable artifact | persistence/provider | **KEEP** for compatibility; surface adapters must not assume submission |
| `src/conversation/steps/generate.py` | Uses `render_artifact_payload()` | ephemeral user-download boundary | **CANONICAL for Telegram** |
| `src/webapp/services/api_client.py` | Calls ephemeral `document/artifact` endpoint | presentation/transport | **CANONICAL for WebApp** |
| `src/delivery/artifact_resolver.py` | Resolves only user-approved durable artifact references | delivery/persistence | **KEEP as explicit durable delivery boundary** |
| `src/storage/*artifact*` | Local/S3 provider adapters | provider dependency | **KEEP behind provider-neutral contract** |

## Architectural conclusion

Splitting the durable artifact stack further would weaken the design because repository metadata, blob bytes, hash verification, artifact state and provider selection form one persistence invariant. They remain separated from business capabilities by interfaces, but are not fragmented into arbitrary micro-modules.

The critical separation is instead:

1. **Document construction/review** — business/capability responsibility.
2. **Ephemeral rendering** — user-download boundary.
3. **Durable artifact persistence** — persistence/provider boundary.
4. **Durable artifact resolution** — delivery boundary.

The WebApp and Telegram surfaces use the ephemeral path where immediate user download is the requirement. Durable storage remains available where an explicit persisted artifact lifecycle is required.

## Security invariants

- Artifact ownership is checked through canonical Case/Document identity.
- Durable delivery requires `USER_APPROVED` state.
- Artifact content SHA-256 is verified before delivery.
- Provider-specific SDKs remain behind `ArtifactBlobStore`.
- Durable storage does not imply transmission, submission, receipt, or acknowledgment.
- No surface may infer government delivery from artifact persistence.

## Branch convergence

The live repository contains exactly nine sanctioned physical branches. No additional active branch requires deletion in this pass. Historical branches are represented by archive tags/evidence and are not counted as active branches.

## Next convergence gate

Before declaring the shared infrastructure production-ready, run fresh CI on the current `main` commit and complete the PostgreSQL durable-provider readiness gate.
