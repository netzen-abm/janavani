# Research, Evidence & Archival Provider Contract

**Status:** Proposed canonical architecture boundary
**Scope:** Academic discovery, open-access retrieval, web archival, provenance-preserving research support

## Purpose

Janavani may need to discover, retrieve, preserve, and cite public research and public web sources while supporting civic evidence workflows. These capabilities must remain provider-neutral and must not make any external project, API, archive, model, or storage system a core dependency.

## Canonical flow

`Research Query / DOI / URL → Discovery → Source Verification → Legal/Public Retrieval → Evidence Registration → Provenance → Optional Archive → Human Review`

## Provider categories

### Scholarly discovery

Providers may include Unpaywall, OpenAlex, Crossref, CORE, institutional repositories, preprint servers, and other lawful open-access indexes.

### Retrieval

Providers may return metadata, abstract/full-text URLs, repository copies, or publicly accessible documents. A provider must not be treated as proof that a document is authentic, current, authoritative, or legally sufficient without separate verification.

### Web archival

Providers may include Internet Archive/Wayback Machine, ArchiveBox, pywb, WARC-based local archives, or other archival services.

### Research tooling / MCP

MCP servers and CLI libraries are integration adapters only. They must not become the domain contract. Their capabilities must be consumable through Janavani's provider-neutral research boundary.

## Evidence rules

1. Open-access availability is not the same as authority or correctness.
2. A retrieved document is not automatically evidence; provenance and source identity must be retained.
3. The system should preserve the original URL/DOI, provider, retrieval timestamp, content hash where feasible, and source metadata.
4. Historical archives should be represented as archived observations/snapshots, not silently substituted for the current source.
5. AI-generated summaries or classifications are assistive outputs and must not be treated as source authority.
6. External retrieval must respect applicable copyright, access-control, robots/publisher terms, API terms, privacy requirements, and rate limits.
7. Janavani must prefer lawful open/public sources and should not implement credential theft, access-control circumvention, or unauthorized paywall bypassing.

## API/provider contract

A provider adapter should expose concepts equivalent to:

- `search(query)`
- `resolve_identifier(identifier)`
- `retrieve_metadata(reference)`
- `list_accessible_locations(reference)`
- `retrieve_public_document(location)`
- `archive_public_source(source)`
- `verify_provenance(source)`

Concrete providers remain replaceable implementations.

## Storage boundary

Research metadata and evidence references must enter Janavani through canonical evidence/repository contracts. Provider SDKs must not write directly into surface-owned persistence.

## Privacy boundary

Research requests may contain sensitive civic context. Provider adapters must support minimization, avoid transmitting unnecessary citizen data, and expose provider/data-processing characteristics where required for informed user choice.

## Recommended initial provider set

Start with provider-neutral adapters for:

1. Unpaywall — open-access location discovery by DOI.
2. OpenAlex — scholarly entity and relationship discovery.
3. Crossref — DOI/metadata resolution where useful.
4. Internet Archive/Wayback — historical public-web snapshots.
5. A WARC/local archival adapter for user-controlled preservation where justified.

ArchiveBox may be evaluated as an implementation behind the archival adapter rather than embedded as a domain dependency.

## Explicit non-goals

- No paywall circumvention implementation.
- No credential/session harvesting.
- No automatic assertion that a retrieved source is authoritative.
- No direct provider calls from Web/Telegram/mobile surface code.
- No mandatory dependency on a single academic index or archive.

## Verification requirements

Before production adoption, each provider must have:

- explicit legal/terms-of-use review;
- rate-limit and failure behavior documented;
- provenance and source identity preserved;
- negative/failure tests;
- provider-independent contract tests;
- graceful degradation when the provider is unavailable;
- no cross-surface lifecycle dependency.
