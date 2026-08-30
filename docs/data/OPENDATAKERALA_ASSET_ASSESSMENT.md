# OpenDataKerala Asset Assessment

## Finding

The OpenDataKerala organization contains datasets that are potentially valuable as **external public-data providers**, especially for Kerala civic geography and infrastructure. They should not be copied into JanaVani as an unqualified source of truth.

## Highest-value repositories identified

### `opendatakerala/lsg-kerala-data`

This repository publishes Kerala Local Self Government spatial data in GeoJSON, JSON, KML and shapefile forms. Its README states that the data are retrieved from OpenStreetMap and maintained as a snapshot by the OpenStreetMap Kerala Community. It also asks that errors be fixed in OpenStreetMap and reported to the repository.

Potential JanaVani uses:

- map/local-body identification;
- Panchayat/Municipality/Corporation boundary lookup;
- jurisdiction inference from a user-selected location;
- offline/cached geospatial reference data;
- spatial cross-checks for authority discovery.

Limitations:

- it is a third-party snapshot, not itself an official government authority directory;
- freshness is a material concern;
- OpenStreetMap-derived administrative boundaries must be treated as geographic reference data, not proof of legal jurisdiction where an official source is required;
- licensing/provenance must be retained.

### `opendatakerala/roads-Kerala`

This repository describes itself as a road-network dataset for Kerala. Its repository includes `Kerala-MDR.csv` and district-level MDR map images.

Potential JanaVani uses:

- help a citizen identify a road/location;
- distinguish or classify a reported road as potentially MDR-related;
- enrich a road-related case before authority discovery;
- support map display and location disambiguation;
- provide context for a complaint/RTI concerning roads.

Limitations:

- repository metadata shows the dataset was updated/pushed in 2024, so it must not be treated as current without freshness validation;
- it should not determine the legally responsible authority by itself;
- road classification and responsibility must ultimately be verified against current authoritative government sources.

## Recommended architecture

Do **not** import these repositories directly into business logic. Add them behind a shared external public-data provider contract:

```text
OpenDataKerala / OSM snapshot
            ↓
External Public Data Provider
            ↓
Provenance + freshness + licence metadata
            ↓
Cross-check / authority verification
            ↓
Shared Civic Capabilities
            ├── Location / jurisdiction
            ├── Authority discovery
            ├── Road context
            └── Map/context presentation
```

## Source hierarchy

For decisions affecting a citizen document:

1. Current official government source / official administrative record
2. Verified government open-data source
3. OpenDataKerala / OSM-derived reference data
4. Citizen-provided information
5. Model/AI inference

OpenDataKerala data may therefore **assist discovery and cross-checking**, but should not silently override a current authoritative source.

## Privacy

These datasets are public geographic/reference data. They should not be combined unnecessarily with private citizen information. Location processing must remain purpose-bound, and precise user location should be collected only when actually needed for the selected capability.

## Shared Infrastructure Gate

**PASS.** A reusable `ExternalPublicDataProvider` capability would allow the same datasets to serve WebApp, Telegram, Mini App and future interfaces without duplicating the data logic.

## Recommendation

Use `lsg-kerala-data` and `roads-Kerala` as **candidate external-provider assets**, not as copied canonical databases. Start with jurisdiction/location enrichment and road-case context after the provider/provenance contract is integrated. Do not make the integration a hard dependency for the core workflow; if the provider is unavailable or stale, JanaVani should degrade to ordinary authority discovery and user-supplied location information.
