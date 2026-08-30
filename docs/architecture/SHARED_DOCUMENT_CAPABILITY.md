# Shared Document Capability

## Purpose

Document generation is a Janavani ecosystem capability, not a Web, Telegram, mobile, or DApp feature.

## Boundary

```text
Access surface
    ↓
DocumentRequest
    ↓
DocumentCapability
    ↓
DocumentProvider
    ↓
DocumentArtifact
```

The capability owns validation and provider routing. Providers own format-specific generation. Access surfaces render results and must not contain document business logic.

## Privacy

Document requests default to `allow_external_processing = false`. A provider must not infer permission to send personal Case/Evidence data externally. Remote processing requires the applicable privacy, consent, minimization, and authorization gates.

## Provider independence

PDF, DOCX, text, local renderers, remote renderers, and future decentralized document providers can implement the same contract. Replacing a provider must not require changes to Case, Evidence, Authority, or access surfaces.

## Current state

This contract is a foundation. Existing generators under `src/documents/` remain candidates for adapter/convergence work and are not declared canonical merely because they exist.

## Completion gate

A production implementation requires provider integration, Case/Evidence/Authority mapping, provenance, privacy tests, format validation, failure/degraded behavior, and end-to-end verification through at least one access surface.
