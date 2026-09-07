# Janavani — Future Ideas Register

**Status:** PARKED — IDEAS / VISION ONLY
**Rule:** Nothing in this document is approved for immediate implementation.
**Purpose:** Preserve useful ideas discovered during architecture/product work without allowing them to expand the current execution scope.

## Operating rule

An idea may be recorded here when it is strategically interesting but does not yet have sufficient evidence, priority, maturity, user demand, security assurance, or implementation readiness.

Before implementation, an item must be promoted through the normal decision process:

```text
Idea → evidence → user/value case → architecture fit → risk review → priority → ADR/spec → implementation
```

## 1. Hardware-backed evidence capture

**Vision:** Make digital evidence capture easier and more trustworthy through native device capabilities and hardware-backed keys where supported.

Potential future capabilities:
- GPS-tagged photo/video capture.
- Capture-time integrity hashing.
- Android Keystore-backed device keys.
- iOS Secure Enclave-backed device keys.
- Device attestation where technically and legally appropriate.
- Capture provenance and transformation history.
- Offline-first evidence capture with later authorized transmission.

**Important constraint:** Hardware-backed integrity must never be represented as proof that the underlying civic claim is true.

**Not for immediate implementation:** Requires threat modelling, platform-specific security review, native integration, recovery design, and evidence-law review.

## 2. Mojo for edge/on-device compute

**Vision:** Evaluate Mojo for narrowly defined high-performance kernels such as local computer vision, OCR preprocessing, media analysis, or future edge inference.

**Architecture rule:** Mojo must remain an optional implementation technology behind stable Janavani contracts. It must not become the canonical domain language or a prerequisite for mobile/Web operation.

**Trigger for reconsideration:** A measured workload where Mojo provides a meaningful benefit over Rust/native/WASM/established inference runtimes.

## 3. Privacy-preserving local AI

**Vision:** Expand local OCR, translation, classification, vision and language capabilities so citizens can receive useful assistance without sending private case/evidence data to remote providers.

Potential future components:
- Local SLM/VLM.
- Local OCR.
- Local translation.
- Local document understanding.
- On-device redaction/scrubbing.
- Private embeddings/indexes.

**Not for immediate implementation:** Model selection, device capability matrix, memory/latency benchmarks, licensing and security evaluation are required first.

## 4. AI trust / deception-resistance evaluation

**Vision:** Establish a Janavani AI Trust Fabric that evaluates model outputs for accuracy, calibration, citation fidelity, sycophancy, misleading behaviour under incentives, data-boundary compliance and action restraint.

Potential future research:
- Representation-based honesty/deception probes.
- Debate/prover-estimator style verification.
- Adversarial evaluation.
- Source-grounded contradiction checks.
- Model/provider comparison.

**Constraint:** Research techniques must not be described as universal lie detectors or guarantees of truthful AI.

## 5. Civic Evidence Passport

**Vision:** A portable, human-readable and machine-verifiable evidence record containing evidence ID, case reference, capture time/location, integrity hash, provenance, transformations, privacy class and attestation state.

Potential future use:
- Case handoff between interfaces.
- User-controlled exports.
- Authorized submissions.
- Independent verification.
- Future decentralized records.

**Constraint:** Clearly distinguish technical integrity from truth, legal admissibility, or official verification.

## 6. User-controlled decentralized infrastructure

**Vision:** Allow citizens to choose decentralized storage, identity, synchronization, networking or verification providers when those providers become mature enough for the relevant capability.

Potential providers/technologies:
- Freenet.
- Nostr.
- IPFS/content-addressed storage.
- Nym/privacy networking.
- Reticulum/mesh networking.
- ZK proofs.
- Future decentralized protocols.

**Architecture rule:** Provider adapters satisfy existing Janavani capability contracts; no provider becomes a mandatory dependency.

## 7. Resilient civic connectivity

**Vision:** Support civic workflows during poor connectivity or infrastructure disruption through offline-first operation, opportunistic synchronization, mesh and potentially satellite-assisted transport.

**Constraint:** Delivery states must remain truthful. No unavailable transport may be reported as successful delivery.

## 8. Biodiversity / species-awareness layer

**Vision:** Introduce a subtle ecological awareness element into Janavani without distracting from civic action.

Possible future placements:
- About/Credits screen.
- First-run contextual line.
- Neutral export footer for general civic exports where appropriate.
- Future location-aware biodiversity education.

**Current recommendation:** Keep formal legal/administrative documents neutral unless the user explicitly chooses an appropriate awareness footer.

## 9. Cross-surface continuity

**Vision:** A citizen can begin a Case in one interface and continue it in another without creating duplicate business state.

Examples:
- Telegram → WebApp.
- WebApp → Android.
- Android → iOS.
- WebApp → DApp.

**Architecture requirement:** Shared Case and capability contracts remain authoritative; interfaces remain independent.

## 10. Capability marketplace / ecosystem participants

**Vision:** In a mature ecosystem, approved third parties such as NGOs, experts, civic researchers, translators, legal-information providers, data providers and technology providers may contribute capabilities without taking ownership of Janavani's core domain.

Potential future mechanisms:
- Capability provider registry.
- Trust/reputation metadata.
- Provider health and versioning.
- Scoped permissions.
- Provenance.
- User choice.

**Not for immediate implementation:** Requires governance, trust, legal, security and commercial models.

## 11. Civic knowledge graph

**Vision:** Build a versioned graph connecting places, jurisdictions, authorities, laws, schemes, offices, documents, cases and public sources.

Potential future benefit:
- Better authority resolution.
- Jurisdiction reasoning.
- Source-aware civic intelligence.
- Cross-case public learning without exposing private citizen data.

**Privacy constraint:** Private Case/Evidence data must never become a public knowledge graph by default.

## 12. Public civic learning layer

**Vision:** Aggregate privacy-preserving, consented and appropriately anonymized civic patterns into public learning and accountability views.

Potential future outputs:
- Issue heatmaps.
- Service-delay patterns.
- Authority response statistics.
- Recurring infrastructure problems.
- Public-interest dashboards.

**Constraint:** Aggregation must not become covert citizen surveillance or expose individual cases.

## 13. Automation as infrastructure

**Vision:** Make testing, provenance checks, security checks, deployment verification, dependency audits and documentation consistency increasingly automated.

**Constraint:** Automation verifies and enforces defined policy; it does not replace human governance for consequential decisions.

## Promotion criteria

A parked idea may enter implementation only when all relevant questions have an evidence-backed answer:

- What citizen problem does it solve?
- Why is the existing capability insufficient?
- Can it reuse an existing contract?
- Does it preserve interface independence?
- Does it preserve user choice?
- Does it preserve privacy/safety by default?
- What happens when it fails?
- What data leaves the device, if any?
- What is the provider/adapter boundary?
- What tests prove completion?
- What legal/security review is required?
- What is the opportunity cost against the current roadmap?

**Until promoted, this register is a parking area—not an implementation queue.**
