# Janavani Shared Capability Catalog

This catalog defines capabilities as reusable infrastructure, independent of access surfaces.

| Capability | Contract | Current state | Future providers/surfaces |
|---|---|---|---|
| Case | CaseRepository | Foundation | Web, mobile, bots, DApp |
| Evidence | EvidenceCapability | Foundation | Local, encrypted sync, IPFS/Freenet adapters |
| Authority | AuthorityCapability | Foundation | Government APIs, verified directories, community providers |
| Document | DocumentCapability | Contract | PDF, DOCX, future formats |
| AI | AICapabilityRouter | Contract | Local, cloud, future models |
| Agentic AI | AgentCapabilityRouter | Contract | Local/cloud/future agents |
| Privacy | Privacy Gateway | Foundation | Every surface/provider |
| Local Vault | LocalVault | Contract + Web provider | Web Crypto/IndexedDB, native secure storage |
| Transport | Provider boundary | Legacy concepts; redesign required | HTTPS, Nym, Reticulum, Freenet/future |

## Rule

A new access surface consumes the catalog. It does not create a parallel implementation of a capability.

## User choice

Capabilities are platform-complete even when a citizen chooses not to invoke them. Availability and user choice are separate concepts.

## Provider plug-and-play

A provider is eligible when it satisfies the relevant contract, privacy/safety policy, tests, health checks, and version compatibility. Provider replacement must not require rewriting consumers.

## Privacy rule

Personal data remains on the user device by default. No personal data is sent to AI or Agentic AI. Encryption does not make personal data permissible to send to AI/agents.
