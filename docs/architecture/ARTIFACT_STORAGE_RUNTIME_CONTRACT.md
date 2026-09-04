# Artifact Storage Runtime Contract

**Status:** CANONICAL RUNTIME SAFETY RULE

## 1. Purpose

Document generation is a shared Janavani capability. Artifact bytes must be
stored through the provider-neutral `ArtifactBlobStore` contract.

No surface may depend on process-local artifact state for production durability.

## 2. Runtime providers

Supported providers are selected through:

`JANAVANI_ARTIFACT_BLOB_PROVIDER`

Current providers:

- `local` — development and controlled single-runtime use;
- `s3` — S3-compatible durable object storage.

Provider-specific SDKs remain inside provider adapters.

## 3. Production rule

A production or multi-instance runtime MUST NOT rely on the default local
storage root under `/tmp` for durable artifacts.

Production configuration must explicitly select a durable blob provider and
configure its credentials/bucket through the runtime secret/configuration
system.

A missing durable provider configuration must fail closed rather than silently
claiming durable storage.

## 4. Metadata versus bytes

Artifact metadata and artifact bytes are separate capabilities:

```text
DocumentDraft
    |
    v
Artifact generation
    |
    +--> DocumentArtifactRepository
    |        metadata/reference
    |
    +--> ArtifactBlobStore
             binary bytes
```

A database record is not proof that the binary artifact is durable, and a blob
object is not by itself the canonical case record.

## 5. User-controlled boundary

Artifact storage exists to support user review, printing and download.
JanaVani does not send or submit generated documents to public authorities.

Storage telemetry must never be interpreted as:

- user sent the document;
- authority received the document;
- authority acknowledged the document.

Those are distinct states and require separate evidence.

## 6. Portability requirement

The canonical artifact reference must use provider-independent metadata.
Provider-specific URLs, SDK objects and response types must not leak into
DocumentDraft, CivicCase, or other domain contracts.

A future provider may implement the same `ArtifactBlobStore` contract without
changing document or case business logic.

## 7. Operational gate

Before production rollout, verify:

1. durable provider selection is explicit;
2. bucket/container credentials are supplied only by runtime configuration;
3. write/read/delete behavior is contract-tested;
4. artifact hashes are preserved;
5. restart does not lose committed artifact bytes;
6. access control and retention policy are defined;
7. metadata and bytes cannot silently diverge;
8. provider failure produces a controlled error;
9. no government submission path exists in the artifact layer.
