# JanaVani — External Ecosystem Asset Audit

Date: 2026-08-30

## Decision summary

| Source | JanaVani value | Current action |
|---|---|---|
| DataPortalIndia / OGD India | HIGH | Adopt as discovery/index layer for government datasets, not as sole authority |
| GitHub Government collection | MEDIUM | Research/design reference only |
| egovernments/Digit-Core | HIGH for architecture/reference | Study and selectively adapt patterns; do not copy platform wholesale |
| egovernments/DIGIT-Frontend | MEDIUM-HIGH for UI architecture | Study reusable UI/micro-frontend/localisation patterns; do not make it a hard dependency |
| DataGov-SamagraX | UNVERIFIED | URL/org was not retrievable in this audit; defer until exact repositories are identified |
| cyb3r-n3rd government-domain gist | HIGH for discovery | Use as non-authoritative discovery list; verify every domain before use |
| samagra-comms/community terms | HIGH for policy/security inspiration | Reference only; do not copy contractual language |
| pritharoy/india-data-sources | HIGH for discovery | Use as a source index, verify each source independently |
| CodeForGoodTech DMP issue #3 | MEDIUM for UX research | Review issue/design findings if accessible; no direct core dependency |

## Key architectural lessons

### DataPortalIndia / OGD India

The Open Government Data Platform India describes itself as a single access point for datasets/apps published by Ministries/Departments. Its GitHub organisation contains examples such as csv-to-api and db-to-api. The csv-to-api repository is a proof-of-concept for dynamically generating REST APIs from static CSV files.

Use: dataset discovery, metadata/catalogue integration, possible ideas for a normalized external-data gateway.

Do not: treat GitHub-hosted OGD code or a third-party mirror as the authoritative legal/public-service source. Current government sources remain authoritative.

### DIGIT

DIGIT-Core is an open-source modular, microservices, multi-tenant public-service platform. Its repository emphasizes unified services/shared logic, loose coupling, master-data management, workflow engine, multilingual support and provider-independent service composition.

These architectural patterns strongly reinforce JanaVani's shared-infrastructure principle. Study them for:
- service boundaries;
- master-data management;
- workflow/state machines;
- configuration-driven capability composition;
- localization;
- reusable public-service modules.

Do not import the entire DIGIT platform. JanaVani has a different product responsibility and must remain citizen-participation focused.

DIGIT-Frontend provides reusable UI components, micro-frontends, shared libraries, localization utilities and configurable governance applications. These are useful references for WebApp/Mini App architecture, but JanaVani should keep its own channel adapters and not make DIGIT a mandatory dependency.

### DataGov-SamagraX

The supplied organization URL could not be resolved through the available GitHub connector and repository search. No integration decision is made until exact repository names are verified.

### Government-domain gist

The cyb3r-n3rd gist is a large list of gov.in domains and explicitly presents itself as a list of Government of India domains. It was last surfaced as a 2021-created gist with later revisions. It is useful as a discovery seed, not as a live authoritative registry. Every domain must be verified against current official sources before use.

### Samagra UCI terms

The provided terms state that users are responsible for data and should not share data with the service unless authorized, describe digital consent responsibilities, and discuss personal-data processing and security. These concepts are useful as policy/design references. JanaVani should develop its own terms/privacy architecture for its own purposes and should not copy contractual language.

### India data-source list

pritharoy/india-data-sources is explicitly a list of publicly available data sources in India and warns contributors not to add unauthorized private/personal data. This aligns strongly with JanaVani's privacy-by-design approach. Use it as a discovery index only; source authority, freshness, licence and applicability must be independently verified.

### GitHub Government collection

Useful for studying established government/open-government patterns and examples. It is not an implementation dependency or authoritative data source.

### CodeForGoodTech DMP issue #3

Use as a UX/product-research reference if the issue content is verified and accessible. The repository is MIT licensed, but license does not imply that its design is suitable for direct reuse in JanaVani. Extract principles, not copied product structure.

## Shared infrastructure rule

All selected assets should plug into a common external-source architecture:

External source → fetcher → normalization → provenance/licence → freshness → verification → shared capability.

No external repository becomes a hidden hard dependency of Telegram, Mini App or WebApp.

## Priority

1. OGD India/DataPortalIndia — dataset discovery and catalogue.
2. DIGIT-Core — architecture and workflow/master-data study.
3. DIGIT-Frontend — reusable UI/localization study.
4. India data-source index + government-domain list — source discovery only.
5. Samagra UCI — policy/security design reference.
6. Government collection + CodeForGoodTech issue — research references.
7. DataGov-SamagraX — revisit after exact repositories are identified.
