# JanaVani — Decentralized & Privacy Technology Assessment

Date: 2026-08-30

## Executive decision

Do not add Freenet, Hyphanet, Nostr, Reticulum, Nym, zero-knowledge proofs, or blockchain infrastructure to the current JanaVani citizen-participation MVP as a mandatory dependency.

Study them as optional shared infrastructure for future public-data distribution, privacy-preserving transport, resilience, integrity, or selective-disclosure capabilities.

## Freenet / Hyphanet

Potential value:
- decentralized distribution of public, non-sensitive civic knowledge;
- resilient replication of public data;
- operation without a single distribution point.

Current decision: research-only / future optional shared capability.

Do not distribute personal or sensitive citizen case evidence through a decentralized public network.

## Nostr

Potential value:
- public civic signals;
- user-controlled public publication;
- decentralized event distribution;
- future public case/outcome signalling when explicitly made public.

Current decision: optional future public-civic distribution layer, never the private case store.

NIPs and protocol implementations must be treated as protocol references; they do not make a published event authoritative.

## Reticulum

Potential value:
- resilient transport over heterogeneous networks;
- potentially useful for future offline/low-connectivity access surfaces.

Current decision: future transport research only. Do not couple the civic core to Reticulum.

## Nym

Potential value:
- privacy-preserving network transport and metadata protection.

Current decision: future optional privacy transport layer. It must not be presented as making an application completely anonymous or eliminating endpoint/device risks.

## Zero-knowledge proofs

Potential value:
- selective disclosure;
- proving a property without revealing the underlying secret;
- future privacy-preserving eligibility or verification flows.

Current decision: future cryptographic capability; not justified for the initial document-generation and civic-routing MVP.

## Blockchain / Hyperledger / Ethereum / Geth

Potential value:
- tamper-evident shared records in multi-party systems;
- future institutional audit or cross-organization coordination.

Current decision: research-only. No blockchain should be introduced merely to store citizen cases or documents. A conventional verifiable audit trail is sufficient for the current product boundary.

## BSA/evidence relationship

Cryptographic integrity may be useful for evidence metadata, but cryptography does not by itself establish legal admissibility or authenticity. Any evidence capability must remain aligned with current Indian law and verified procedural requirements.

## Privacy rule

Private/sensitive citizen material remains on the user's device by default. Decentralized/public networks may only receive explicitly public, non-sensitive material through a separate consented capability.

## Shared Infrastructure Gate

All technologies above pass as candidates for shared infrastructure only when implemented behind provider-neutral interfaces. None is a core dependency of the civic reasoning engine.

## Recommended future capability map

Public Civic Distribution → Nostr/Freenet/Hyphanet candidates.
Privacy Transport → Nym/Reticulum candidates.
Selective Disclosure → Zero-knowledge candidates.
Integrity/Audit → Cryptographic evidence/audit candidates.
Institutional Shared Ledger → Hyperledger/Ethereum candidates only if a real multi-party requirement emerges.
