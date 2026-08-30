# JanaVani — External Ecosystem Asset Audit

Date: 2026-08-30

## Decision summary

| Source | JanaVani value | Current action |
|---|---|---|
| DataPortalIndia / OGD India | HIGH | Adopt as discovery/index layer for government datasets, not as sole authority |
| project-open-data | MEDIUM-HIGH | Study open-data metadata/catalogue patterns; no runtime dependency yet |
| GitHub Government collection | MEDIUM | Research/design reference only |
| egovernments/Digit-Core | HIGH for architecture/reference | Study and selectively adapt patterns; do not copy platform wholesale |
| egovernments/DIGIT-Frontend | MEDIUM-HIGH for UI architecture | Study reusable UI/micro-frontend/localisation patterns; do not make it a hard dependency |
| DataGov-SamagraX | UNVERIFIED | URL/org was not retrievable in this audit; defer until exact repositories are identified |
| cyb3r-n3rd government-domain gist | HIGH for discovery | Use as non-authoritative discovery list; verify every domain before use |
| samagra-comms/community terms | HIGH for policy/security inspiration | Reference only; do not copy contractual language |
| pritharoy/india-data-sources | HIGH for discovery | Use as a source index, verify each source independently |
| CodeForGoodTech DMP issue #3 | MEDIUM for UX research | Review issue/design findings if accessible; no direct core dependency |
| Bhuvan / NRSC data services | HIGH for geospatial/contextual use cases | Research/adapter candidate; verify current endpoints, access terms, rate limits, provenance and licence before production |
| ISRO GitHub | LOW for current JanaVani | No direct integration; revisit only for a concrete civic-use case |
| brenykurien/bhuvan_web_services | MEDIUM for technical study | Third-party implementation reference only; verify current Bhuvan services independently |
| brenykurien metadata.txt | MEDIUM for technical study | Reference metadata only; not authoritative API specification |

## Key architectural lessons

### DataPortalIndia / OGD India

The Open Government Data Platform India is useful as a dataset discovery and catalogue layer. Its GitHub organisation contains examples such as csv-to-api and db-to-api. The csv-to-api repository is a proof-of-concept for dynamically generating REST APIs from static CSV files.

Use: dataset discovery, metadata/catalogue integration, ideas for normalized external-data access.

Do not: treat GitHub-hosted OGD code or a third-party mirror as the authoritative legal/public-service source. Current government sources remain authoritative.

### project-open-data

Useful as a reference for open-data metadata/catalogue conventions and machine-readable dataset discovery. Keep it at the architecture/research layer until a concrete reusable component is identified.

### DIGIT

DIGIT-Core is an open-source modular, microservices, multi-tenant public-service platform. Its repository emphasizes unified services/shared logic, loose coupling, master-data management, workflow engine, multilingual support and provider-independent service composition.

These architectural patterns strongly reinforce JanaVani's shared-infrastructure principle. Study them for service boundaries, master data, workflow/state machines, configuration-driven capability composition, localization and reusable public-service modules.

Do not import the entire DIGIT platform. JanaVani has a different product responsibility and must remain citizen-participation focused.

DIGIT-Frontend provides reusable UI components, micro-frontends, shared libraries, localization utilities and configurable governance applications. These are useful references for WebApp/Mini App architecture, but JanaVani should keep its own channel adapters and not make DIGIT a mandatory dependency.

### DataGov-SamagraX

The supplied organization URL could not be resolved through the available GitHub connector and repository search. No integration decision is made until exact repository names are verified.

### Government-domain gist

The cyb3r-n3rd gist is a large list of gov.in domains and explicitly presents itself as a list of Government of India domains. It is useful as a discovery seed, not as a live authoritative registry. Every domain must be verified against current official sources before use.

### Samagra UCI terms

The provided terms state that users are responsible for data and should not share data with the service unless authorized, describe digital consent responsibilities, and discuss personal-data processing and security. These concepts are useful as policy/design references. JanaVani should develop its own terms/privacy architecture for its own purposes and should not copy contractual language.

### India data-source list

pritharoy/india-data-sources is useful as a discovery index for publicly available Indian data sources. Use it as an index only; source authority, freshness, licence and applicability must be independently verified.

### GitHub Government collection

Useful for studying established government/open-government patterns and examples. It is not an implementation dependency or authoritative data source.

### CodeForGoodTech DMP issue #3

Use as a UX/product-research reference if the issue content is verified and accessible. The repository is MIT licensed, but license does not imply that its design is suitable for direct reuse in JanaVani. Extract principles, not copied product structure.

### Bhuvan / NRSC

Potentially high-value for location and geospatial context: map layers, imagery, administrative geography and other earth-observation-derived information could help certain civic cases. Use must be capability-driven, not dataset-driven.

Bhuvan/NRSC should be treated as a contextual provider. It should not determine legal responsibility by itself. The production adapter must verify current service availability, data semantics, terms/licence, rate limits and provenance. The official Bhuvan/NRSC service should be preferred over third-party wrappers.

### ISRO GitHub

The currently discoverable `isro/api` repository is an open API for ISRO spacecraft, launchers, customer satellites, centres and missions. fileciteturn623file0L2-L2 This is not part of normal civic routing and therefore should not become a current JanaVani dependency.

### brenykurien/bhuvan_web_services

Useful as implementation research for interacting with Bhuvan web services. It is third-party code, so it must not be treated as the authoritative definition of current Bhuvan endpoints or semantics.

### metadata.txt

Useful for examining metadata/service notes documented by that third-party integration. Treat as a reference artifact only and independently verify all current endpoint, field and service assumptions.

## Shared infrastructure rule

All selected assets should plug into a common external-source architecture:

External source → fetcher → normalization → provenance/licence → freshness → verification → shared capability.

No external repository becomes a hidden hard dependency of Telegram, Mini App or WebApp.

## Priority

1. Kerala LSG / OpenDataKerala.
2. Kerala roads / OpenDataKerala.
3. Bhuvan/NRSC for concrete geospatial civic use cases.
4. OGD India/DataPortalIndia for dataset discovery and catalogue.
5. project-open-data metadata/catalogue patterns.
6. DIGIT-Core architecture and workflow/master-data study.
7. DIGIT-Frontend UI/localization study.
8. India data-source index + government-domain list for source discovery.
9. Samagra UCI for policy/security reference.
10. Government collection + CodeForGoodTech issue for research.
11. ISRO and other specialized sources only when tied to a specific civic capability.
